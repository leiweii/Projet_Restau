from django.core.exceptions import ValidationError
from django.db import transaction

from reservations.models import Reservation, ReservationDayLock

from .availability import generate_candidate_slots, is_slot_available


@transaction.atomic
def create_reservation(data, *, user=None):
    day = data["date"]
    start_time = data["heure"]
    party_size = data["nombre_personnes"]

    lock, _ = ReservationDayLock.objects.get_or_create(date=day)
    ReservationDayLock.objects.select_for_update().get(pk=lock.pk)

    if start_time not in generate_candidate_slots(day, party_size):
        raise ValidationError(
            "Cet horaire n'est pas disponible selon les heures d'ouverture."
        )
    if not is_slot_available(day, start_time, party_size):
        raise ValidationError(
            "Ce créneau vient de devenir complet. Choisissez un autre horaire."
        )

    reservation_data = {
        field: data.get(field)
        for field in (
            "nom",
            "email",
            "telephone",
            "date",
            "heure",
            "nombre_personnes",
            "commentaire",
        )
    }
    if user is not None and user.is_authenticated:
        reservation_data["user"] = user
    return Reservation.objects.create(**reservation_data)
