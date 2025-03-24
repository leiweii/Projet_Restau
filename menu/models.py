from django.db import models

class Categorie(models.Model):
    nom = models.CharField(max_length=50)

    def __str__(self):
        return self.nom

class Plat(models.Model):
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    prix = models.DecimalField(max_digits=6, decimal_places=2)
    disponible = models.BooleanField(default=True)
    image = models.ImageField(upload_to='plats/', blank=True, null=True)

    def __str__(self):
        return f"{self.nom} ({self.prix}€)"
