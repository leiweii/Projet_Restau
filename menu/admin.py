from django.contrib import admin
from .models import Categorie, Plat, Allergene

@admin.register(Allergene)
class AllergeneAdmin(admin.ModelAdmin):
    list_display = ['nom']

@admin.register(Plat)
class PlatAdmin(admin.ModelAdmin):
    list_display = ['nom', 'categorie', 'prix', 'disponible']
    list_filter = ['categorie', 'disponible', 'allergenes']
    search_fields = ['nom']
    filter_horizontal = ['allergenes'] 
