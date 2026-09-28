from django.core import mail
from django.core.mail.backends.base import BaseEmailBackend
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from reservations.models import Reservation
from restaurant.models import WeeklyOpeningHours


class FailingEmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        raise OSError("SMTP indisponible")


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="reservations@osaka.test",
    PATRON_EMAIL="restaurant@osaka.test",
)
class ReservationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="client",
            password="test123",
        )
        self.client.login(username="client", password="test123")
        WeeklyOpeningHours.objects.create(
            weekday=WeeklyOpeningHours.TUESDAY,
            opens_at="19:00",
            closes_at="22:30",
        )

    def booking_data(self):
        return {
            "nom": "Jean",
            "email": "jean@example.com",
            "telephone": "0612345678",
            "date": "2030-12-24",
            "heure": "19:30",
            "nombre_personnes": 2,
        }

    def test_creer_reservation(self):
        response = self.client.post(reverse("reserver"), self.booking_data())

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Reservation.objects.filter(nom="Jean").exists())
        self.assertEqual(len(mail.outbox), 2)

    @override_settings(
        EMAIL_BACKEND=(
            "reservations.tests.test_reservations.FailingEmailBackend"
        )
    )
    def test_email_failure_keeps_confirmed_reservation_and_confirmation_page(self):
        response = self.client.post(reverse("reserver"), self.booking_data())

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reservations/confirmation.html")
        self.assertContains(response, "Merci pour votre réservation")
        self.assertEqual(Reservation.objects.filter(nom="Jean").count(), 1)
