from django.contrib import admin
from .models import Categorie, Plat, Ingredient

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['nom']

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['nom']
    search_fields = ['nom']

@admin.register(Plat)
class PlatAdmin(admin.ModelAdmin):
    list_display = ['nom', 'categorie', 'prix', 'disponible', 'get_ingredients']
    list_filter = ['categorie', 'disponible']
    search_fields = ['nom', 'description']
    filter_horizontal = ['ingredients']  

    def get_ingredients(self, obj):
        return ", ".join([i.nom for i in obj.ingredients.all()])
    get_ingredients.short_description = "Ingrédients"
