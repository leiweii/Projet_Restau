from django.contrib import admin
from .models import Reservation, HoraireSpecial

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('nom', 'date', 'heure', 'nombre_personnes', 'email', 'telephone')
    list_filter = ('date', 'heure')
    search_fields = ('nom', 'email', 'telephone')


@admin.register(HoraireSpecial)
class HoraireSpecialAdmin(admin.ModelAdmin):
    list_display = ('date', 'ferme', 'ouverture', 'fermeture', 'description')
    list_filter = ('ferme',)
