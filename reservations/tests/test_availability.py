from datetime import date, datetime, time

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from restaurant.models import (
    RestaurantSettings,
    SpecialOpeningHours,
    WeeklyOpeningHours,
)
from reservations.models import Reservation
from reservations.services.availability import (
    generate_candidate_slots,
    is_slot_available,
)


class SlotGenerationTests(TestCase):
    def setUp(self):
        self.config = RestaurantSettings.load()
        self.config.reservation_duration_minutes = 90
        self.config.slot_interval_minutes = 30
        self.config.modification_cutoff_hours = 2
        self.config.max_online_party_size = 8
        self.config.save()
        WeeklyOpeningHours.objects.create(
            weekday=WeeklyOpeningHours.MONDAY,
            opens_at=time(12, 0),
            closes_at=time(14, 30),
        )
        WeeklyOpeningHours.objects.create(
            weekday=WeeklyOpeningHours.MONDAY,
            opens_at=time(19, 0),
            closes_at=time(22, 30),
        )
        self.future_monday = date(2030, 12, 23)
        self.now = timezone.make_aware(datetime(2030, 12, 20, 10, 0))

    def test_generates_interval_slots_that_fit_the_full_stay(self):
        slots = generate_candidate_slots(
            self.future_monday,
            party_size=2,
            now=self.now,
        )

        self.assertEqual(
            slots,
            [
                time(12, 0),
                time(12, 30),
                time(13, 0),
                time(19, 0),
                time(19, 30),
                time(20, 0),
                time(20, 30),
                time(21, 0),
            ],
        )

    def test_exceptional_closure_returns_no_slots(self):
        SpecialOpeningHours.objects.create(
            date=self.future_monday,
            closed=True,
        )

        self.assertEqual(
            generate_candidate_slots(self.future_monday, 2, now=self.now),
            [],
        )

    def test_exceptional_opening_replaces_weekly_hours(self):
        SpecialOpeningHours.objects.create(
            date=self.future_monday,
            closed=False,
            opens_at=time(18, 0),
            closes_at=time(21, 0),
        )

        self.assertEqual(
            generate_candidate_slots(self.future_monday, 2, now=self.now),
            [time(18, 0), time(18, 30), time(19, 0), time(19, 30)],
        )

    def test_past_date_returns_no_slots(self):
        self.assertEqual(
            generate_candidate_slots(date(2030, 12, 16), 2, now=self.now),
            [],
        )

    def test_slots_inside_minimum_delay_are_excluded(self):
        same_day_now = timezone.make_aware(datetime(2030, 12, 23, 11, 0))

        slots = generate_candidate_slots(
            self.future_monday,
            2,
            now=same_day_now,
        )

        self.assertEqual(slots[0], time(13, 0))

    def test_party_size_outside_online_limit_is_rejected(self):
        for party_size in (0, 9):
            with self.subTest(party_size=party_size):
                with self.assertRaises(ValidationError):
                    generate_candidate_slots(
                        self.future_monday,
                        party_size,
                        now=self.now,
                    )


class CapacityTests(TestCase):
    def setUp(self):
        self.config = RestaurantSettings.load()
        self.config.capacity = 20
        self.config.reservation_duration_minutes = 90
        self.config.max_online_party_size = 8
        self.config.save()
        self.day = date(2030, 12, 23)

    def reserve(self, at, people):
        return Reservation.objects.create(
            nom="Client test",
            email="client@example.com",
            telephone="0102030405",
            date=self.day,
            heure=at,
            nombre_personnes=people,
        )

    def test_exact_capacity_is_available(self):
        self.reserve(time(12, 0), 12)

        self.assertTrue(is_slot_available(self.day, time(13, 0), 8))

    def test_capacity_exceeded_during_overlap_is_unavailable(self):
        self.reserve(time(12, 0), 12)
        self.reserve(time(12, 30), 1)

        self.assertFalse(is_slot_available(self.day, time(13, 0), 8))

    def test_reservation_ending_at_candidate_start_does_not_overlap(self):
        self.reserve(time(11, 30), 20)

        self.assertTrue(is_slot_available(self.day, time(13, 0), 8))

    def test_non_simultaneous_overlaps_are_not_incorrectly_summed(self):
        self.reserve(time(12, 0), 8)
        self.reserve(time(14, 0), 8)

        self.assertTrue(is_slot_available(self.day, time(13, 0), 8))

    def test_reservation_can_be_excluded_during_modification(self):
        current = self.reserve(time(13, 0), 18)

        self.assertTrue(
            is_slot_available(
                self.day,
                time(13, 0),
                8,
                exclude_reservation=current,
            )
        )
