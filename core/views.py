from django.shortcuts import render
from datetime import date
from reservations.models import HoraireSpecial

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
