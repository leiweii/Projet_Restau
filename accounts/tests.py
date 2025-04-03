from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

class UserAccountTests(TestCase):
    def test_user_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'password_confirm': 'password123'
        })
        self.assertEqual(response.status_code, 302)  # Redirection post inscription
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_user_login(self):
        User.objects.create_user(username='user1', password='pass123')
        response = self.client.post(reverse('login'), {
            'username': 'user1',
            'password': 'pass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirection vers profil
