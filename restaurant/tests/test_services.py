from datetime import date, time

from django.test import TestCase

from restaurant.models import SpecialOpeningHours, WeeklyOpeningHours
from restaurant.services import get_effective_intervals, get_opening_summary


class OpeningHoursServiceTests(TestCase):
    def setUp(self):
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

    def test_weekly_services_are_returned_in_time_order(self):
        intervals = get_effective_intervals(date(2030, 12, 23))

        self.assertEqual(
            intervals,
            [(time(12, 0), time(14, 30)), (time(19, 0), time(22, 30))],
        )

    def test_exceptional_closure_overrides_weekly_services(self):
        SpecialOpeningHours.objects.create(
            date=date(2030, 12, 23),
            closed=True,
            description="Fermeture annuelle",
        )

        self.assertEqual(get_effective_intervals(date(2030, 12, 23)), [])
        self.assertEqual(
            get_opening_summary(date(2030, 12, 23)),
            "Fermé exceptionnellement — Fermeture annuelle",
        )

    def test_exceptional_opening_replaces_weekly_services(self):
        SpecialOpeningHours.objects.create(
            date=date(2030, 12, 23),
            closed=False,
            opens_at=time(18, 0),
            closes_at=time(21, 0),
        )

        self.assertEqual(
            get_effective_intervals(date(2030, 12, 23)),
            [(time(18, 0), time(21, 0))],
        )

    def test_summary_formats_all_services(self):
        self.assertEqual(
            get_opening_summary(date(2030, 12, 23)),
            "12h00–14h30 / 19h00–22h30",
        )
