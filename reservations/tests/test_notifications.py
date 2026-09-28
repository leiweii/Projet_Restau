from datetime import date, time
from smtplib import SMTPException
from unittest.mock import patch

from django.core import mail
from django.test import RequestFactory, TestCase, override_settings

from reservations.models import Reservation
from reservations.services.notifications import send_reservation_notifications


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="reservations@osaka.test",
    PATRON_EMAIL="restaurant@osaka.test",
)
class ReservationNotificationTests(TestCase):
    def setUp(self):
        self.reservation = Reservation.objects.create(
            nom="Camille",
            email="camille@example.com",
            telephone="0102030405",
            date=date(2030, 12, 23),
            heure=time(12, 30),
            nombre_personnes=4,
        )
        self.request = RequestFactory().get("/reservations/reserver/")

    def test_sends_client_summary_with_absolute_management_link(self):
        result = send_reservation_notifications(self.reservation, self.request)

        self.assertTrue(result.client_sent)
        self.assertTrue(result.restaurant_sent)
        self.assertEqual(len(mail.outbox), 2)
        client_message = mail.outbox[0]
        self.assertEqual(client_message.to, ["camille@example.com"])
        self.assertIn("23/12/2030", client_message.body)
        self.assertIn("12:30", client_message.body)
        self.assertIn("4 personnes", client_message.body)
        self.assertIn(
            f"http://testserver/reservations/gerer/"
            f"{self.reservation.management_token}/",
            client_message.body,
        )

    def test_client_failure_does_not_prevent_restaurant_attempt(self):
        with patch(
            "reservations.services.notifications.send_mail",
            side_effect=[SMTPException("client failure"), 1],
        ) as mocked_send, self.assertLogs(
            "reservations.notifications", level="ERROR"
        ) as captured:
            result = send_reservation_notifications(self.reservation, self.request)

        self.assertFalse(result.client_sent)
        self.assertTrue(result.restaurant_sent)
        self.assertEqual(mocked_send.call_count, 2)
        logs = " ".join(captured.output)
        self.assertIn(f"reservation_id={self.reservation.pk}", logs)
        self.assertNotIn(self.reservation.email, logs)
        self.assertNotIn(self.reservation.telephone, logs)
