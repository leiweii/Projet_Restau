from django.db import models

class Categorie(models.Model):
    nom = models.CharField(max_length=50)

    def __str__(self):
        return self.nom

class Ingredient(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

    

class Plat(models.Model):
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    prix = models.DecimalField(max_digits=6, decimal_places=2)
    disponible = models.BooleanField(default=True)
    image = models.ImageField(upload_to='plats/', blank=True, null=True)

    ingredients = models.ManyToManyField(Ingredient, blank=True)

    def __str__(self):
        return f"{self.nom} ({self.prix}€)"



from decimal import Decimal

class MenuPromotionnel(models.Model):
    nom = models.CharField(max_length=100, unique= 'true')
    plat_principal = models.ForeignKey(Plat, related_name='menus_principal', on_delete=models.CASCADE)
    plat_associe = models.ForeignKey(Plat, related_name='menus_associes', on_delete=models.CASCADE)

    def prix_total(self):
        prix = self.plat_principal.prix + self.plat_associe.prix
        return round(prix * Decimal('0.8'), 2)

    def __str__(self):
        return f"{self.nom} – {self.plat_principal.nom} + {self.plat_associe.nom}"
