from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Reservation

class ReservationTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="client", password="test123")
        self.client.login(username="client", password="test123")

    def test_creer_reservation(self):
        response = self.client.post(reverse('reserver'), {
            'nom': 'Jean',
            'email': 'jean@example.com',
            'telephone': '0612345678',
            'date': '2030-12-24',
            'heure': '19:30',
            'nombre_personnes': 2
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Reservation.objects.filter(nom='Jean').exists())
