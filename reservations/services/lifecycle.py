from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from restaurant.models import RestaurantSettings
from reservations.models import Reservation, ReservationDayLock

from .availability import generate_candidate_slots, is_slot_available


def _aware_arrival(reservation):
    arrival = datetime.combine(reservation.date, reservation.heure)
    return timezone.make_aware(arrival, timezone.get_current_timezone())


def _validate_customer_action(reservation, now):
    if not can_customer_manage(reservation, now=now):
        config = RestaurantSettings.load()
        if reservation.status != Reservation.Status.CONFIRMED:
            raise ValidationError("Cette réservation ne peut plus être modifiée.")
        raise ValidationError(
            f"La modification ou l'annulation doit être effectuée au moins "
            f"{config.modification_cutoff_hours} heures avant l'arrivée."
        )


def can_customer_manage(reservation, *, now=None):
    if reservation.status != Reservation.Status.CONFIRMED:
        return False
    now = now or timezone.now()
    config = RestaurantSettings.load()
    return now + timedelta(
        hours=config.modification_cutoff_hours
    ) <= _aware_arrival(reservation)


def _lock_days(*days):
    for day in sorted(set(days)):
        lock, _ = ReservationDayLock.objects.get_or_create(date=day)
        ReservationDayLock.objects.select_for_update().get(pk=lock.pk)


@transaction.atomic
def update_reservation(reservation, data, *, now=None):
    now = now or timezone.now()
    reservation = Reservation.objects.select_for_update().get(pk=reservation.pk)
    _validate_customer_action(reservation, now)

    new_day = data["date"]
    new_time = data["heure"]
    party_size = data["nombre_personnes"]
    _lock_days(reservation.date, new_day)

    if new_time not in generate_candidate_slots(new_day, party_size, now=now):
        raise ValidationError(
            "Cet horaire n'est pas disponible selon les heures d'ouverture."
        )
    if not is_slot_available(
        new_day,
        new_time,
        party_size,
        exclude_reservation=reservation,
    ):
        raise ValidationError(
            "Ce créneau vient de devenir complet. Choisissez un autre horaire."
        )

    for field in (
        "nom",
        "email",
        "telephone",
        "date",
        "heure",
        "nombre_personnes",
        "commentaire",
    ):
        setattr(reservation, field, data.get(field))
    reservation.save()
    return reservation


@transaction.atomic
def cancel_reservation(reservation, *, now=None, staff_override=False):
    now = now or timezone.now()
    reservation = Reservation.objects.select_for_update().get(pk=reservation.pk)
    if not staff_override:
        _validate_customer_action(reservation, now)
    elif reservation.status == Reservation.Status.CANCELLED:
        return reservation

    _lock_days(reservation.date)
    reservation.status = Reservation.Status.CANCELLED
    reservation.save(update_fields=["status", "updated_at"])
    return reservation
