from django import forms
from .models import Reservation

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['nom', 'email', 'telephone', 'date', 'heure', 'nombre_personnes', 'commentaire']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'heure': forms.TimeInput(attrs={'type': 'time', 'id': 'id_heure'}),
        }


# class CommandeForm(forms.ModelForm):
#     class Meta:
#         model = Commande
#         fields = ['nom', 'telephone', 'date', 'heure_retrait', 'plats', 'commentaire']
#         widgets = {
#             'date': forms.DateInput(attrs={'type': 'date'}),
#             'heure_retrait': forms.TimeInput(attrs={'type': 'time'}),
#             'plats': forms.CheckboxSelectMultiple()
#         }
