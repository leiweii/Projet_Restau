from datetime import time

from django.core.exceptions import ValidationError
from django.test import TestCase

from restaurant.models import RestaurantSettings, WeeklyOpeningHours


class RestaurantSettingsTests(TestCase):
    def test_defaults_match_approved_reservation_rules(self):
        config = RestaurantSettings.load()

        self.assertEqual(config.capacity, 20)
        self.assertEqual(config.reservation_duration_minutes, 90)
        self.assertEqual(config.slot_interval_minutes, 30)
        self.assertEqual(config.modification_cutoff_hours, 2)
        self.assertEqual(config.max_online_party_size, 8)

    def test_load_always_returns_the_same_configuration(self):
        first = RestaurantSettings.load()
        second = RestaurantSettings.load()

        self.assertEqual(first.pk, second.pk)
        self.assertEqual(RestaurantSettings.objects.count(), 1)


class WeeklyOpeningHoursTests(TestCase):
    def test_end_time_must_be_after_start_time(self):
        hours = WeeklyOpeningHours(
            weekday=WeeklyOpeningHours.MONDAY,
            opens_at=time(14, 0),
            closes_at=time(12, 0),
        )

        with self.assertRaises(ValidationError):
            hours.full_clean()

    def test_services_for_the_same_day_cannot_overlap(self):
        WeeklyOpeningHours.objects.create(
            weekday=WeeklyOpeningHours.MONDAY,
            opens_at=time(12, 0),
            closes_at=time(14, 30),
        )
        overlapping = WeeklyOpeningHours(
            weekday=WeeklyOpeningHours.MONDAY,
            opens_at=time(14, 0),
            closes_at=time(16, 0),
        )

        with self.assertRaises(ValidationError):
            overlapping.full_clean()

    def test_separate_services_for_the_same_day_are_allowed(self):
        WeeklyOpeningHours.objects.create(
            weekday=WeeklyOpeningHours.MONDAY,
            opens_at=time(12, 0),
            closes_at=time(14, 30),
        )
        evening = WeeklyOpeningHours(
            weekday=WeeklyOpeningHours.MONDAY,
            opens_at=time(19, 0),
            closes_at=time(22, 30),
        )

        evening.full_clean()
