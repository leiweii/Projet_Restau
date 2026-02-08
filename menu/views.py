from django.shortcuts import render
from .models import Categorie, Plat
from django.db.models import Q

def menu_view(request):
    categories = Categorie.objects.all()

    # Get params
    categorie_id = request.GET.get('categorie')
    recherche = request.GET.get('recherche','')
    tri_prix = request.GET.get('prix')

    plats = Plat.objects.filter(disponible=True)

    if categorie_id and categorie_id != 'all':
        plats = plats.filter(categorie_id=categorie_id)

    if recherche:
        plats = plats.filter(Q(nom__icontains=recherche) | Q(description__icontains=recherche))

    if tri_prix == 'asc':
        plats = plats.order_by('prix')
    elif tri_prix == 'desc':
        plats = plats.order_by('-prix')

    return render(request, 'menu/menu.html', {
        'categories': categories,
        'plats': plats,
        'categorie_id': categorie_id,
        'recherche': recherche,
        'tri_prix': tri_prix,
    })


from .models import MenuPromotionnel

def promotions_view(request):
    menus = MenuPromotionnel.objects.select_related('plat_principal', 'plat_associe')
    return render(request, 'menu/promotions.html', {'menus': menus})