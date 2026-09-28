from datetime import date, datetime, time

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from restaurant.models import (
    RestaurantSettings,
    SpecialOpeningHours,
    WeeklyOpeningHours,
)
from reservations.services.availability import generate_candidate_slots


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
