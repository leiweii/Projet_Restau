from django.core.management import call_command
from django.test import TestCase

from restaurant.models import RestaurantSettings, WeeklyOpeningHours


class SeedRestaurantCommandTests(TestCase):
    def test_command_is_idempotent_and_preserves_the_displayed_schedule(self):
        call_command("seed_restaurant", verbosity=0)
        call_command("seed_restaurant", verbosity=0)

        config = RestaurantSettings.load()
        self.assertEqual(config.city, "Créteil")
        self.assertEqual(WeeklyOpeningHours.objects.count(), 12)
