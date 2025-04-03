from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

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


