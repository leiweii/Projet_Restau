from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from restaurant.models import RestaurantSettings, WeeklyOpeningHours

class DashboardAccessTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='adminpass', is_staff=True)
        self.user = User.objects.create_user(username='client', password='clientpass')

    def test_admin_access_dashboard(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_client_access_dashboard(self):
        self.client.login(username='client', password='clientpass')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)


class PublicRestaurantInformationTests(TestCase):
    def setUp(self):
        config = RestaurantSettings.load()
        config.name = "Osaka Test"
        config.address = "10 rue du Test"
        config.save()
        WeeklyOpeningHours.objects.create(
            weekday=WeeklyOpeningHours.MONDAY,
            opens_at="12:00",
            closes_at="14:30",
        )

    def test_home_uses_database_backed_restaurant_information(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, "Osaka Test")
        self.assertContains(response, "10 rue du Test")

    def test_contact_uses_database_backed_weekly_schedule(self):
        response = self.client.get(reverse("contact"))

        self.assertContains(response, "Lundi")
        self.assertContains(response, "12h00–14h30")


