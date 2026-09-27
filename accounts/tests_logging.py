import logging

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase

from .middleware import RequestLoggingMiddleware


class RequestLoggingMiddlewareTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User(username="private-user", email="private@example.com")

    def make_request(self, status_code=200):
        request = self.factory.get(
            "/menu/",
            REMOTE_ADDR="192.0.2.1",
            HTTP_X_FORWARDED_FOR="198.51.100.2",
        )
        request.user = self.user
        middleware = RequestLoggingMiddleware(
            lambda received_request: HttpResponse(status=status_code)
        )
        return middleware(request)

    def test_success_log_contains_operational_fields_only(self):
        with self.assertLogs("django.request", level=logging.INFO) as captured:
            self.make_request()

        message = captured.output[-1]
        self.assertIn("GET", message)
        self.assertIn("/menu/", message)
        self.assertIn("200", message)
        self.assertNotIn(self.user.username, message)
        self.assertNotIn(self.user.email, message)
        self.assertNotIn("192.0.2.1", message)
        self.assertNotIn("198.51.100.2", message)

    def test_error_response_uses_error_level(self):
        with self.assertLogs("django.request", level=logging.INFO) as captured:
            self.make_request(status_code=500)

        self.assertEqual(captured.records[-1].levelname, "ERROR")

    def test_middleware_emits_one_record_per_request(self):
        with self.assertLogs("django.request", level=logging.INFO) as captured:
            self.make_request()

        self.assertEqual(len(captured.records), 1)
