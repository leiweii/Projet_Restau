from django import forms
from .models import Plat, Categorie

class PlatForm(forms.ModelForm):
    class Meta:
        model = Plat
        fields = ['nom', 'categorie', 'description', 'prix', 'disponible', 'image']


class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['nom']
