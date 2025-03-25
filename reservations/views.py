from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ReservationForm
from .models import Reservation, HoraireSpecial
from django.contrib import messages
from django.core.mail import send_mail
from datetime import date
from django.conf import settings
from django.shortcuts import get_object_or_404


def reserver_view(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            date_reservation = form.cleaned_data['date']

            # 🔒 Vérifie fermeture exceptionnelle
            special = HoraireSpecial.objects.filter(date=date_reservation).first()
            if special and special.ferme:
                messages.error(request, "⚠️ Le restaurant est exceptionnellement fermé à cette date.")
                return render(request, 'reservations/reserver.html', {'form': form})

            # 💾 Création réservation
            reservation = form.save(commit=False)
            if request.user.is_authenticated:
                reservation.user = request.user
            reservation.save()

            # ✅ Email de confirmation
            objet = "Confirmation de votre réservation"
            message = f"""
Bonjour {reservation.nom},

Votre réservation a bien été enregistrée pour le {reservation.date.strftime('%d/%m/%Y')} à {reservation.heure}.
Nombre de personnes : {reservation.nombre_personnes}

Merci et à bientôt !

– Restaurant OSAKA
"""
            send_mail(
                objet,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [reservation.email],
                fail_silently=False,
            )

            messages.success(request, "Votre réservation a bien été enregistrée ✅")
            return render(request, 'reservations/confirmation.html', {'reservation': reservation})
    else:
        # Pré-remplissage pour utilisateur connecté
        initial = {}
        if request.user.is_authenticated:
            initial = {
                'nom': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
                'telephone': request.user.profile.telephone
            }
        form = ReservationForm(initial=initial)

    return render(request, 'reservations/reserver.html', {'form': form})



@login_required
def mes_reservations_view(request):
    reservations = Reservation.objects.filter(user=request.user).order_by('-date')
    return render(request, 'reservations/mes_reservations.html', {'reservations': reservations})



@login_required
def modifier_reservation_view(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)

    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            messages.success(request, "Réservation modifiée avec succès.")
            return redirect('mes_reservations')
    else:
        form = ReservationForm(instance=reservation)

    return render(request, 'reservations/modifier_reservation.html', {'form': form})

@login_required
def supprimer_reservation_view(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)

    if request.method == 'POST':
        reservation.delete()
        messages.success(request, "Réservation annulée.")
        return redirect('mes_reservations')

    return render(request, 'reservations/confirmer_suppression.html', {'reservation': reservation})
