import logging
from dataclasses import dataclass

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse


logger = logging.getLogger("reservations.notifications")


@dataclass(frozen=True)
class NotificationResult:
    client_sent: bool
    restaurant_sent: bool


def _deliver(subject, message, recipient, reservation_id, recipient_type):
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False,
        )
    except Exception:
        logger.error(
            "reservation_notification_failed reservation_id=%s recipient_type=%s",
            reservation_id,
            recipient_type,
        )
        return False
    return True


def send_reservation_notifications(reservation, request):
    management_path = reverse(
        "guest_reservation",
        args=[reservation.management_token],
    )
    management_url = request.build_absolute_uri(management_path)
    formatted_date = reservation.date.strftime("%d/%m/%Y")
    formatted_time = reservation.heure.strftime("%H:%M")

    client_message = (
        f"Bonjour {reservation.nom},\n\n"
        f"Votre réservation est confirmée pour le {formatted_date} à "
        f"{formatted_time}, pour {reservation.nombre_personnes} personnes.\n\n"
        f"Gérer ou annuler votre réservation : {management_url}\n\n"
        "Merci et à bientôt !\n\nRestaurant Osaka"
    )
    restaurant_message = (
        "Nouvelle réservation confirmée\n\n"
        f"Nom : {reservation.nom}\n"
        f"Date : {formatted_date}\n"
        f"Heure : {formatted_time}\n"
        f"Nombre de personnes : {reservation.nombre_personnes}\n"
        f"Téléphone : {reservation.telephone}\n"
        f"Email : {reservation.email}\n"
        f"Réservation : #{reservation.pk}"
    )

    client_sent = _deliver(
        "Confirmation de votre réservation",
        client_message,
        reservation.email,
        reservation.pk,
        "client",
    )
    restaurant_sent = _deliver(
        "Nouvelle réservation – Osaka",
        restaurant_message,
        settings.PATRON_EMAIL,
        reservation.pk,
        "restaurant",
    )
    return NotificationResult(
        client_sent=client_sent,
        restaurant_sent=restaurant_sent,
    )
