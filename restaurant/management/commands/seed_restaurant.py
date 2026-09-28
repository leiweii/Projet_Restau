from datetime import time

from django.core.management.base import BaseCommand

from restaurant.models import RestaurantSettings, WeeklyOpeningHours


class Command(BaseCommand):
    help = "Initialise les informations et horaires déjà affichés par le projet."

    def handle(self, *args, **options):
        config = RestaurantSettings.load()
        config.name = "Restaurant Osaka"
        config.address = "1 Rue Claude Vasconi"
        config.postal_code = "94000"
        config.city = "Créteil"
        config.public_phone = "01 77 20 86 83"
        config.public_email = "contact@restaurant.com"
        config.save()

        services = []
        for weekday in range(5):
            services.extend(
                (
                    (weekday, time(12, 0), time(14, 30)),
                    (weekday, time(19, 0), time(22, 30)),
                )
            )
        services.extend(
            (
                (WeeklyOpeningHours.SATURDAY, time(19, 0), time(22, 30)),
                (WeeklyOpeningHours.SUNDAY, time(19, 0), time(22, 30)),
            )
        )

        for weekday, opens_at, closes_at in services:
            WeeklyOpeningHours.objects.get_or_create(
                weekday=weekday,
                opens_at=opens_at,
                closes_at=closes_at,
            )

        self.stdout.write(self.style.SUCCESS("Restaurant et horaires initialisés."))
