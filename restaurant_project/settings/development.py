from .base import *  # noqa: F403


SECRET_KEY = "django-insecure-development-only-restaurant-osaka-key"
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "Restaurant Osaka <noreply@localhost>"
PATRON_EMAIL = "patron@localhost"
