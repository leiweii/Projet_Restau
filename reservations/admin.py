from django.contrib import admin
from .models import Reservation

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('nom', 'date', 'heure', 'nombre_personnes', 'email', 'telephone')
    list_filter = ('date', 'heure')
    search_fields = ('nom', 'email', 'telephone')
