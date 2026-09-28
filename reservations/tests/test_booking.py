from datetime import date, time

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from restaurant.models import RestaurantSettings, WeeklyOpeningHours
from reservations.models import Reservation
from reservations.services.booking import create_reservation


class BookingServiceTests(TestCase):
    def setUp(self):
        config = RestaurantSettings.load()
        config.capacity = 20
        config.max_online_party_size = 8
        config.save()
        WeeklyOpeningHours.objects.create(
            weekday=WeeklyOpeningHours.MONDAY,
            opens_at=time(12, 0),
            closes_at=time(14, 30),
        )
        self.day = date(2030, 12, 23)
        self.data = {
            "nom": "Camille",
            "email": "camille@example.com",
            "telephone": "0102030405",
            "date": self.day,
            "heure": time(12, 30),
            "nombre_personnes": 4,
            "commentaire": "Anniversaire",
        }

    def test_open_slot_is_created(self):
        reservation = create_reservation(self.data)

        self.assertIsNotNone(reservation.pk)
        self.assertEqual(reservation.nombre_personnes, 4)

    def test_closed_time_is_rejected(self):
        invalid = {**self.data, "heure": time(16, 0)}

        with self.assertRaises(ValidationError):
            create_reservation(invalid)

        self.assertFalse(Reservation.objects.exists())

    def test_slot_that_became_full_is_rejected(self):
        Reservation.objects.create(**{**self.data, "nombre_personnes": 18})

        with self.assertRaises(ValidationError):
            create_reservation(self.data)

        self.assertEqual(Reservation.objects.count(), 1)


class AvailabilityEndpointTests(TestCase):
    def setUp(self):
        RestaurantSettings.load()
        WeeklyOpeningHours.objects.create(
            weekday=WeeklyOpeningHours.MONDAY,
            opens_at=time(12, 0),
            closes_at=time(14, 30),
        )

    def test_endpoint_returns_available_times(self):
        response = self.client.get(
            reverse("reservation_availability"),
            {"date": "2030-12-23", "personnes": "2"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["slots"], ["12:00", "12:30", "13:00"])

    def test_endpoint_returns_explicit_validation_error(self):
        response = self.client.get(
            reverse("reservation_availability"),
            {"date": "date-invalide", "personnes": "2"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())
