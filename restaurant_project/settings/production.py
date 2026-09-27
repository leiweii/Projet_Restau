from .base import *  # noqa: F403
from .env import env_bool, env_list, env_value


SECRET_KEY = env_value("DJANGO_SECRET_KEY", required=True)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS")
if not ALLOWED_HOSTS:
    from django.core.exceptions import ImproperlyConfigured

    raise ImproperlyConfigured(
        "The environment variable DJANGO_ALLOWED_HOSTS is required."
    )

DEBUG = False

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env_value("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(env_value("EMAIL_PORT", "587"))
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
EMAIL_HOST_USER = env_value("EMAIL_HOST_USER", required=True)
EMAIL_HOST_PASSWORD = env_value("EMAIL_HOST_PASSWORD", required=True)
PATRON_EMAIL = env_value("PATRON_EMAIL", required=True)
DEFAULT_FROM_EMAIL = env_value("DEFAULT_FROM_EMAIL", required=True)

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31_536_000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
