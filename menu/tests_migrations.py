from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class MenuPromotionnelUniqueMigrationTests(TransactionTestCase):
    migrate_from = [("menu", "0004_menupromotionnel")]
    migrate_to = [("menu", "0005_alter_menupromotionnel_nom")]

    def setUp(self):
        super().setUp()
        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_from)
        old_apps = executor.loader.project_state(self.migrate_from).apps

        Categorie = old_apps.get_model("menu", "Categorie")
        Plat = old_apps.get_model("menu", "Plat")
        MenuPromotionnel = old_apps.get_model("menu", "MenuPromotionnel")

        categorie = Categorie.objects.create(nom="Menus")
        dragon_roll = Plat.objects.create(
            nom="dragon roll saumon cheese",
            prix="8.20",
            categorie=categorie,
        )
        edamame = Plat.objects.create(
            nom="Edamame",
            prix="5.50",
            categorie=categorie,
        )
        futomaki = Plat.objects.create(
            nom="futomaki",
            prix="10.00",
            categorie=categorie,
        )
        nems = Plat.objects.create(
            nom="Nêms au poulet 🐔",
            prix="6.30",
            categorie=categorie,
        )

        MenuPromotionnel.objects.create(
            id=2,
            nom="SHI",
            plat_principal=dragon_roll,
            plat_associe=edamame,
        )
        MenuPromotionnel.objects.create(
            id=4,
            nom="SHI",
            plat_principal=futomaki,
            plat_associe=nems,
        )

        executor = MigrationExecutor(connection)
        executor.migrate(self.migrate_to)
        self.apps = executor.loader.project_state(self.migrate_to).apps

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        super().tearDown()

    def test_duplicate_promotions_are_preserved_with_descriptive_names(self):
        MenuPromotionnel = self.apps.get_model("menu", "MenuPromotionnel")

        names_by_id = dict(
            MenuPromotionnel.objects.filter(id__in=(2, 4)).values_list(
                "id", "nom"
            )
        )

        self.assertEqual(
            names_by_id,
            {2: "Menu Dragon Roll", 4: "Menu Futomaki"},
        )
