import logging
import time

logger = logging.getLogger('django.request')

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.monotonic()
        response = self.get_response(request)
        duration_ms = round((time.monotonic() - start_time) * 1000)
        log_method = logger.error if response.status_code >= 400 else logger.info
        log_method(
            "request_completed method=%s path=%s status_code=%s duration_ms=%s",
            request.method,
            request.path,
            response.status_code,
            duration_ms,
        )

        return response
