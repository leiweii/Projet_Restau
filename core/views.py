from datetime import date
from reservations.models import HoraireSpecial
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from reservations.models import Reservation, HoraireSpecial
from menu.models import Plat, Categorie
from django.db.models import Q



def contact_view(request):
    today = date.today()
    fermeture_message = None

    special = HoraireSpecial.objects.filter(date=today).first()
    if special and special.ferme:
        fermeture_message = f"⚠️ Le restaurant est exceptionnellement fermé aujourd’hui ({today.strftime('%d/%m/%Y')})."

    horaires = {
        'Lundi': 'Fermé',
        'Mardi': '12h00 - 14h00 / 19h00 - 22h00',
        'Mercredi': '12h00 - 14h00 / 19h00 - 22h00',
        'Jeudi': '12h00 - 14h00 / 19h00 - 22h00',
        'Vendredi': '12h00 - 14h00 / 19h00 - 22h30',
        'Samedi': '12h00 - 14h30 / 19h00 - 22h30',
        'Dimanche': '12h00 - 14h30 / 19h00 - 22h00',
    }

    return render(request, 'core/contact.html', {
        'fermeture_message': fermeture_message,
        'horaires': horaires
    })



def home_view(request):
    return render(request, 'core/home.html')




# 限定只允许管理员访问
def admin_required(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(admin_required)
def dashboard_home(request):
    search = request.GET.get('search', '')
    reservations = Reservation.objects.all().order_by('-date')

    if search:
        reservations = reservations.filter(
            Q(nom__icontains=search) |
            Q(telephone__icontains=search) |
            Q(email__icontains=search)
        )

    plats = Plat.objects.select_related('categorie').all()

    return render(request, 'core/dashboard.html', {
        'reservations': reservations,
        'plats': plats,
        'search': search,
    })
