from datetime import date, time
from uuid import uuid4

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from restaurant.models import WeeklyOpeningHours
from reservations.models import Reservation


class GuestReservationManagementTests(TestCase):
    def setUp(self):
        self.reservation = Reservation.objects.create(
            nom="Invité",
            email="guest@example.com",
            telephone="0102030405",
            date=date(2030, 12, 23),
            heure=time(12, 0),
            nombre_personnes=2,
        )
        WeeklyOpeningHours.objects.create(
            weekday=WeeklyOpeningHours.MONDAY,
            opens_at=time(12, 0),
            closes_at=time(14, 30),
        )

    def test_guest_can_open_management_page_with_token(self):
        response = self.client.get(
            reverse("guest_reservation", args=[self.reservation.management_token])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invité")

    def test_past_reservation_does_not_offer_actions(self):
        self.reservation.date = date(2020, 12, 23)
        self.reservation.save(update_fields=["date"])

        response = self.client.get(
            reverse("guest_reservation", args=[self.reservation.management_token])
        )

        self.assertNotContains(response, ">Modifier<")
        self.assertNotContains(response, ">Annuler<")

    def test_unknown_token_returns_not_found(self):
        response = self.client.get(reverse("guest_reservation", args=[uuid4()]))

        self.assertEqual(response.status_code, 404)

    def test_guest_can_cancel_from_private_link(self):
        response = self.client.post(
            reverse(
                "guest_cancel_reservation",
                args=[self.reservation.management_token],
            )
        )

        self.assertRedirects(
            response,
            reverse("guest_reservation", args=[self.reservation.management_token]),
        )
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.status, Reservation.Status.CANCELLED)


class MemberReservationManagementTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user("owner", password="secret123")
        self.other = User.objects.create_user("other", password="secret123")
        self.reservation = Reservation.objects.create(
            user=self.owner,
            nom="Membre",
            email="member@example.com",
            telephone="0102030405",
            date=date(2030, 12, 23),
            heure=time(12, 0),
            nombre_personnes=2,
        )

    def test_member_cancellation_preserves_record(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("supprimer_reservation", args=[self.reservation.pk])
        )

        self.assertRedirects(response, reverse("mes_reservations"))
        self.reservation.refresh_from_db()
        self.assertEqual(self.reservation.status, Reservation.Status.CANCELLED)

    def test_other_member_cannot_manage_reservation(self):
        self.client.force_login(self.other)

        response = self.client.get(
            reverse("modifier_reservation", args=[self.reservation.pk])
        )

        self.assertEqual(response.status_code, 404)
