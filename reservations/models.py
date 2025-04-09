from django.db import models
from django.contrib.auth.models import User
from menu.models import Plat

class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    nom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    date = models.DateField()
    heure = models.TimeField()
    nombre_personnes = models.PositiveIntegerField()
    commentaire = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} - {self.date} à {self.heure} ({self.nombre_personnes} pers.)"
    

# class Commande(models.Model):
#     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
#     nom = models.CharField(max_length=100)
#     telephone = models.CharField(max_length=20)
#     date = models.DateField()
#     heure_retrait = models.TimeField()
#     plats = models.ManyToManyField(Plat)
#     commentaire = models.TextField(blank=True)
#     date_creation = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Commande {self.nom} le {self.date} à {self.heure_retrait}"



class HoraireSpecial(models.Model):
    date = models.DateField(unique=True)
    ferme = models.BooleanField(default=True)
    ouverture = models.TimeField(blank=True, null=True)
    fermeture = models.TimeField(blank=True, null=True)
    description = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.date} – {'Fermé' if self.ferme else 'Ouvert exceptionnellement'}"
