from django import forms
from .models import Plat, Categorie, Allergene

class PlatForm(forms.ModelForm):
    class Meta:
        model = Plat
        fields = ['nom', 'categorie', 'description', 'prix', 'disponible', 'image', 'allergenes']
        widgets = {
            'allergenes': forms.CheckboxSelectMultiple()
        }



class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['nom']


class AllergeneForm(forms.ModelForm):
    class Meta:
        model = Allergene
        fields = ['nom']
