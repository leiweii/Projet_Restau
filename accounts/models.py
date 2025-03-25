from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telephone = models.CharField(max_length=10, blank=True)
    preferences = models.TextField(blank=True)

    def __str__(self):
        return f"Profil de {self.user.username}"
