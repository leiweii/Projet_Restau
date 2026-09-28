from datetime import date, time

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class SpecialOpeningHoursMigrationTests(TransactionTestCase):
    migrate_from = [
        ("restaurant", "0001_initial"),
        ("reservations", "0002_horairespecial"),
    ]
    migrate_to = [
        ("restaurant", "0002_specialopeninghours"),
        ("reservations", "0002_horairespecial"),
    ]

    def setUp(self):
        super().setUp()
        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_from)
        old_apps = executor.loader.project_state(self.migrate_from).apps
        LegacyHours = old_apps.get_model("reservations", "HoraireSpecial")
        LegacyHours.objects.create(
            date=date(2030, 12, 24),
            ferme=False,
            ouverture=time(18, 30),
            fermeture=time(22, 0),
            description="Service de Noël",
        )

        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_to)
        self.apps = executor.loader.project_state(self.migrate_to).apps

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_existing_special_hours_are_copied_without_data_loss(self):
        SpecialHours = self.apps.get_model("restaurant", "SpecialOpeningHours")

        copied = SpecialHours.objects.get(date=date(2030, 12, 24))
        self.assertFalse(copied.closed)
        self.assertEqual(copied.opens_at, time(18, 30))
        self.assertEqual(copied.closes_at, time(22, 0))
        self.assertEqual(copied.description, "Service de Noël")
