from django import forms
from .models import Plat, Categorie, Ingredient

class PlatForm(forms.ModelForm):
    class Meta:
        model = Plat
        fields = ['nom', 'categorie', 'description', 'prix', 'disponible', 'image', 'ingredients']
        widgets = {
            'ingredients': forms.CheckboxSelectMultiple()
        }




class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['nom']



class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['nom']

