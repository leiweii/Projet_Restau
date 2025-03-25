from django import forms
from .models import Reservation, HoraireSpecial

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['nom', 'email', 'telephone', 'date', 'heure', 'nombre_personnes', 'commentaire']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'heure': forms.TimeInput(attrs={'type': 'time'}),
        }



class HoraireSpecialForm(forms.ModelForm):
    class Meta:
        model = HoraireSpecial
        fields = ['date', 'ferme', 'ouverture', 'fermeture', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'ouverture': forms.TimeInput(attrs={'type': 'time'}),
            'fermeture': forms.TimeInput(attrs={'type': 'time'}),
        }
