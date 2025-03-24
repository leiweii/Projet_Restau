from django.shortcuts import render
from .models import Categorie

def menu_view(request):
    categories = Categorie.objects.prefetch_related('plat_set').all()
    return render(request, 'menu/menu.html', {'categories': categories})
