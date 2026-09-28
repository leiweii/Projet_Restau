from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ReservationForm
from .models import Reservation
from django.contrib import messages
from django.core.mail import send_mail
from datetime import date
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.http import JsonResponse

from .services.availability import generate_available_slots
from .services.booking import create_reservation
from .services.lifecycle import (
    can_customer_manage,
    cancel_reservation,
    update_reservation,
)


def reserver_view(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            try:
                reservation = create_reservation(
                    form.cleaned_data,
                    user=request.user,
                )
            except ValidationError as error:
                form.add_error(None, error)
                return render(request, 'reservations/reserver.html', {'form': form})

            # ✅ Email de confirmation client
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

            # 📩 Email au patron
            message_pour_patron = f"""
Nouvelle réservation enregistrée :

👤 Nom : {reservation.nom}
📅 Date : {reservation.date.strftime('%d/%m/%Y')}
🕒 Heure : {reservation.heure}
👥 Nombre de personnes : {reservation.nombre_personnes}
📞 Téléphone : {reservation.telephone}
📧 Email : {reservation.email}
"""
            send_mail(
                "📌 Nouvelle réservation – OSAKA",
                message_pour_patron,
                settings.DEFAULT_FROM_EMAIL,
                [settings.PATRON_EMAIL],
                fail_silently=False,
            )

            messages.success(request, "Votre réservation a bien été enregistrée ✅")
            return render(request, 'reservations/confirmation.html', {'reservation': reservation})

    else:
        # Pré-remplissage si connecté
        initial = {}
        if request.user.is_authenticated:
            initial = {
                'nom': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
                'telephone': request.user.profile.telephone
            }
        form = ReservationForm(initial=initial)

    return render(request, 'reservations/reserver.html', {'form': form})


def availability_view(request):
    try:
        day = date.fromisoformat(request.GET.get("date", ""))
        party_size = int(request.GET.get("personnes", ""))
        slots = generate_available_slots(day, party_size)
    except (TypeError, ValueError, ValidationError) as error:
        message = error.messages[0] if isinstance(error, ValidationError) else (
            "Indiquez une date et un nombre de personnes valides."
        )
        return JsonResponse({"error": message}, status=400)

    return JsonResponse(
        {"slots": [slot.strftime("%H:%M") for slot in slots]}
    )



# def commander_view(request):
#     if request.method == 'POST':
#         form = CommandeForm(request.POST)
#         if form.is_valid():
#             commande = form.save(commit=False)
#             if request.user.is_authenticated:
#                 commande.user = request.user
#             commande.save()
#             form.save_m2m()
#             return render(request, 'reservations/confirmation_commande.html', {'commande': commande})
#     else:
#         form = CommandeForm()
#     return render(request, 'reservations/commander.html', {'form': form})



@login_required
def mes_reservations_view(request):
    reservations = Reservation.objects.filter(user=request.user).order_by('-date')
    manageable_ids = {
        reservation.pk
        for reservation in reservations
        if can_customer_manage(reservation)
    }
    return render(
        request,
        'reservations/mes_reservations.html',
        {'reservations': reservations, 'manageable_ids': manageable_ids},
    )



@login_required
def modifier_reservation_view(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)

    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            try:
                update_reservation(reservation, form.cleaned_data)
            except ValidationError as error:
                form.add_error(None, error)
            else:
                messages.success(request, "Réservation modifiée avec succès.")
                return redirect('mes_reservations')
    else:
        form = ReservationForm(instance=reservation)

    return render(request, 'reservations/modifier_reservation.html', {'form': form})

@login_required
def supprimer_reservation_view(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)

    if request.method == 'POST':
        try:
            cancel_reservation(reservation)
        except ValidationError as error:
            messages.error(request, error.messages[0])
        else:
            messages.success(request, "Réservation annulée.")
            return redirect('mes_reservations')

    return render(request, 'reservations/confirmer_suppression.html', {'reservation': reservation})


def guest_reservation_view(request, token):
    reservation = get_object_or_404(Reservation, management_token=token)
    return render(
        request,
        "reservations/guest_management.html",
        {
            "reservation": reservation,
            "can_manage": can_customer_manage(reservation),
        },
    )


def guest_modify_reservation_view(request, token):
    reservation = get_object_or_404(Reservation, management_token=token)
    if request.method == "POST":
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            try:
                update_reservation(reservation, form.cleaned_data)
            except ValidationError as error:
                form.add_error(None, error)
            else:
                messages.success(request, "Réservation modifiée avec succès.")
                return redirect("guest_reservation", token=token)
    else:
        form = ReservationForm(instance=reservation)
    return render(
        request,
        "reservations/guest_modify.html",
        {"form": form, "reservation": reservation},
    )


def guest_cancel_reservation_view(request, token):
    reservation = get_object_or_404(Reservation, management_token=token)
    if request.method == "POST":
        try:
            cancel_reservation(reservation)
        except ValidationError as error:
            messages.error(request, error.messages[0])
        else:
            messages.success(request, "Réservation annulée.")
        return redirect("guest_reservation", token=token)
    return render(
        request,
        "reservations/guest_cancel.html",
        {"reservation": reservation},
    )
