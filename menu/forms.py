from django import forms
from .models import Plat, Categorie, Ingredient
from .models import MenuPromotionnel

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




class MenuPromoForm(forms.ModelForm):
    class Meta:
        model = MenuPromotionnel
        fields = ['nom', 'plat_associe', 'plat_principal']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['plat_associe'].queryset = Plat.objects.filter(
            categorie__nom__iexact="🎟 Entrées"
        ).order_by('nom')

        self.fields['plat_principal'].queryset = Plat.objects.filter(
            categorie__nom__in=["🍣 SUSHI", "🍣 SASHIMI","🍙 TÉMAKI"]
        ).order_by('nom')