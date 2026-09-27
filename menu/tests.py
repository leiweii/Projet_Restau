from django.test import TestCase
from django.db import IntegrityError, transaction
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Categorie, MenuPromotionnel

class CategorieTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username="admin", password="adminpass", is_staff=True)
        self.client.login(username="admin", password="adminpass")

    def test_ajout_categorie(self):
        response = self.client.post(reverse('categorie_create'), {
            'nom': 'Desserts'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Categorie.objects.filter(nom='Desserts').exists())


from django.test import TestCase
from .models import Plat, Categorie, Ingredient

class MenuTests(TestCase):
    def setUp(self):
        self.categorie = Categorie.objects.create(nom="Plats chauds")
        self.ingredient = Ingredient.objects.create(nom="Saumon")

    def test_creer_un_plat(self):
        """✅ Créer un plat avec un ingrédient et une catégorie"""
        plat = Plat.objects.create(
            nom="Sushi saumon",
            description="Délicieux sushi au saumon frais",
            prix=12.50,
            categorie=self.categorie
        )
        plat.ingredients.add(self.ingredient)
        self.assertEqual(plat.nom, "Sushi saumon")
        self.assertIn(self.ingredient, plat.ingredients.all())


class MenuPromotionnelConstraintTests(TestCase):
    def setUp(self):
        self.categorie = Categorie.objects.create(nom="Menus")
        self.plat_principal = Plat.objects.create(
            nom="Sushi",
            prix="12.00",
            categorie=self.categorie,
        )
        self.plat_associe = Plat.objects.create(
            nom="Soupe",
            prix="4.00",
            categorie=self.categorie,
        )

    def menu_data(self):
        return {
            "nom": "Menu Osaka",
            "plat_principal": self.plat_principal,
            "plat_associe": self.plat_associe,
        }

    def test_nom_unique_metadata_is_boolean_true(self):
        field = MenuPromotionnel._meta.get_field("nom")
        self.assertIs(field.unique, True)

    def test_duplicate_nom_is_rejected_by_database(self):
        MenuPromotionnel.objects.create(**self.menu_data())

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                MenuPromotionnel.objects.create(**self.menu_data())
