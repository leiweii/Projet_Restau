from datetime import date, datetime, time

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from restaurant.models import RestaurantSettings, WeeklyOpeningHours
from reservations.models import Reservation
from reservations.services.availability import is_slot_available
from reservations.services.lifecycle import cancel_reservation, update_reservation


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


class ReservationLifecycleServiceTests(TestCase):
    def setUp(self):
        config = RestaurantSettings.load()
        config.capacity = 20
        config.reservation_duration_minutes = 90
        config.modification_cutoff_hours = 2
        config.max_online_party_size = 8
        config.save()
        WeeklyOpeningHours.objects.create(
            weekday=WeeklyOpeningHours.MONDAY,
            opens_at=time(12, 0),
            closes_at=time(14, 30),
        )
        self.reservation = Reservation.objects.create(
            nom="Client test",
            email="client@example.com",
            telephone="0102030405",
            date=date(2030, 12, 23),
            heure=time(12, 0),
            nombre_personnes=2,
        )

    def now(self, hour):
        return timezone.make_aware(datetime(2030, 12, 23, hour, 0))

    def reservation_data(self, **overrides):
        data = {
            "nom": self.reservation.nom,
            "email": self.reservation.email,
            "telephone": self.reservation.telephone,
            "date": self.reservation.date,
            "heure": time(12, 30),
            "nombre_personnes": self.reservation.nombre_personnes,
            "commentaire": "Table calme",
        }
        data.update(overrides)
        return data

    def test_customer_can_modify_before_cutoff(self):
        updated = update_reservation(
            self.reservation,
            self.reservation_data(),
            now=self.now(9),
        )

        self.assertEqual(updated.heure, time(12, 30))
        self.assertEqual(updated.commentaire, "Table calme")

    def test_customer_cannot_modify_inside_cutoff(self):
        with self.assertRaisesMessage(ValidationError, "2 heures"):
            update_reservation(
                self.reservation,
                self.reservation_data(),
                now=self.now(11),
            )

    def test_modification_rechecks_capacity(self):
        Reservation.objects.create(
            nom="Grand groupe",
            email="group@example.com",
            telephone="0102030406",
            date=self.reservation.date,
            heure=time(12, 30),
            nombre_personnes=19,
        )

        with self.assertRaisesMessage(ValidationError, "complet"):
            update_reservation(
                self.reservation,
                self.reservation_data(nombre_personnes=2),
                now=self.now(9),
            )

    def test_customer_cancellation_changes_status_without_deleting(self):
        cancel_reservation(self.reservation, now=self.now(9))

        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.status, Reservation.Status.CANCELLED)
        self.assertTrue(Reservation.objects.filter(pk=self.reservation.pk).exists())

    def test_customer_cannot_cancel_inside_cutoff_but_staff_can(self):
        with self.assertRaisesMessage(ValidationError, "2 heures"):
            cancel_reservation(self.reservation, now=self.now(11))

        cancel_reservation(self.reservation, now=self.now(11), staff_override=True)
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.status, Reservation.Status.CANCELLED)
