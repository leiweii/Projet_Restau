from datetime import date, time

from django.test import TestCase

from restaurant.models import RestaurantSettings
from reservations.models import Reservation
from reservations.services.availability import is_slot_available


class ReservationLifecycleModelTests(TestCase):
    def reservation(self, **overrides):
        data = {
            "nom": "Client test",
            "email": "client@example.com",
            "telephone": "0102030405",
            "date": date(2030, 12, 23),
            "heure": time(12, 0),
            "nombre_personnes": 2,
        }
        data.update(overrides)
        return Reservation.objects.create(**data)

    def test_new_reservation_is_confirmed_with_unique_management_token(self):
        first = self.reservation()
        second = self.reservation(email="other@example.com")

        self.assertEqual(first.status, Reservation.Status.CONFIRMED)
        self.assertIsNotNone(first.management_token)
        self.assertNotEqual(first.management_token, second.management_token)

    def test_cancelled_reservation_does_not_consume_capacity(self):
        config = RestaurantSettings.load()
        config.capacity = 20
        config.reservation_duration_minutes = 90
        config.max_online_party_size = 8
        config.save()
        self.reservation(
            nombre_personnes=20,
            status=Reservation.Status.CANCELLED,
        )

        self.assertTrue(
            is_slot_available(date(2030, 12, 23), time(12, 30), 8)
        )

    def test_confirmed_reservation_still_consumes_capacity(self):
        config = RestaurantSettings.load()
        config.capacity = 20
        config.reservation_duration_minutes = 90
        config.max_online_party_size = 8
        config.save()
        self.reservation(nombre_personnes=20)

        self.assertFalse(
            is_slot_available(date(2030, 12, 23), time(12, 30), 8)
        )
