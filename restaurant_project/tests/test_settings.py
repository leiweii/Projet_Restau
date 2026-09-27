import os
import subprocess
import sys
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase

from restaurant_project.settings.env import env_bool, env_list, env_value


class EnvironmentHelperTests(SimpleTestCase):
    def test_required_value_names_missing_variable(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesMessage(ImproperlyConfigured, "DJANGO_SECRET_KEY"):
                env_value("DJANGO_SECRET_KEY", required=True)

    def test_boolean_false_values_are_false(self):
        for value in ("0", "false", "no", "off", "FALSE"):
            with self.subTest(value=value), patch.dict(
                os.environ, {"FLAG": value}, clear=True
            ):
                self.assertIs(env_bool("FLAG", default=True), False)

    def test_list_removes_whitespace_and_empty_items(self):
        with patch.dict(
            os.environ,
            {"HOSTS": " osaka.fr, www.osaka.fr, "},
            clear=True,
        ):
            self.assertEqual(env_list("HOSTS"), ["osaka.fr", "www.osaka.fr"])


class SettingsModuleTests(SimpleTestCase):
    def run_settings_script(self, module, script, **environment):
        command = f"import {module} as settings; {script}"
        process_environment = os.environ.copy()
        for name in (
            "DJANGO_SECRET_KEY",
            "DJANGO_ALLOWED_HOSTS",
            "EMAIL_HOST_USER",
            "EMAIL_HOST_PASSWORD",
            "PATRON_EMAIL",
            "DEFAULT_FROM_EMAIL",
        ):
            process_environment.pop(name, None)
        process_environment.update(environment)
        return subprocess.run(
            [sys.executable, "-c", command],
            capture_output=True,
            text=True,
            env=process_environment,
            check=False,
        )

    def test_production_requires_secret_key(self):
        result = self.run_settings_script(
            "restaurant_project.settings.production",
            "print(settings.DEBUG)",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DJANGO_SECRET_KEY", result.stderr)

    def test_production_requires_allowed_hosts(self):
        result = self.run_settings_script(
            "restaurant_project.settings.production",
            "print(settings.DEBUG)",
            DJANGO_SECRET_KEY="test-secret",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("DJANGO_ALLOWED_HOSTS", result.stderr)

    def test_production_enables_https_and_secure_cookies(self):
        result = self.run_settings_script(
            "restaurant_project.settings.production",
            "assert settings.DEBUG is False; "
            "assert settings.ALLOWED_HOSTS == ['example.com']; "
            "assert settings.SECURE_SSL_REDIRECT is True; "
            "assert settings.SESSION_COOKIE_SECURE is True; "
            "assert settings.CSRF_COOKIE_SECURE is True",
            DJANGO_SECRET_KEY=("test-only-secret-" * 4),
            DJANGO_ALLOWED_HOSTS="example.com",
            EMAIL_HOST_USER="test@example.com",
            EMAIL_HOST_PASSWORD="test-password",
            PATRON_EMAIL="owner@example.com",
            DEFAULT_FROM_EMAIL="noreply@example.com",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_development_uses_console_email_backend(self):
        result = self.run_settings_script(
            "restaurant_project.settings.development",
            "assert settings.EMAIL_BACKEND == "
            "'django.core.mail.backends.console.EmailBackend'",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_development_uses_europe_paris_timezone(self):
        result = self.run_settings_script(
            "restaurant_project.settings.development",
            "assert settings.TIME_ZONE == 'Europe/Paris'",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
