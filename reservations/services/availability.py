from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone

from restaurant.models import RestaurantSettings
from restaurant.services import get_effective_intervals
from reservations.models import Reservation


def _aware_datetime(day, value):
    combined = datetime.combine(day, value)
    return timezone.make_aware(combined, timezone.get_current_timezone())


def validate_party_size(party_size, config=None):
    config = config or RestaurantSettings.load()
    if party_size < 1:
        raise ValidationError("Le nombre de personnes doit être au moins égal à 1.")
    if party_size > config.max_online_party_size:
        raise ValidationError(
            f"Pour plus de {config.max_online_party_size} personnes, "
            "contactez directement le restaurant."
        )
    return config


def generate_candidate_slots(day, party_size, *, now=None):
    config = validate_party_size(party_size)
    now = now or timezone.now()
    if timezone.is_naive(now):
        now = timezone.make_aware(now, timezone.get_current_timezone())

    earliest = now + timedelta(hours=config.modification_cutoff_hours)
    duration = timedelta(minutes=config.reservation_duration_minutes)
    interval = timedelta(minutes=config.slot_interval_minutes)
    slots = []

    for opens_at, closes_at in get_effective_intervals(day):
        current = _aware_datetime(day, opens_at)
        service_end = _aware_datetime(day, closes_at)
        while current + duration <= service_end:
            if current >= earliest:
                slots.append(current.time().replace(tzinfo=None))
            current += interval

    return slots


def is_slot_available(
    day,
    start_time,
    party_size,
    *,
    exclude_reservation=None,
):
    config = validate_party_size(party_size)
    candidate_start = _aware_datetime(day, start_time)
    duration = timedelta(minutes=config.reservation_duration_minutes)
    candidate_end = candidate_start + duration

    reservations = Reservation.objects.filter(date=day)
    if exclude_reservation is not None and exclude_reservation.pk:
        reservations = reservations.exclude(pk=exclude_reservation.pk)

    events = []
    for reservation in reservations.only("heure", "nombre_personnes"):
        reservation_start = _aware_datetime(day, reservation.heure)
        reservation_end = reservation_start + duration
        if reservation_start < candidate_end and reservation_end > candidate_start:
            events.append(
                (max(reservation_start, candidate_start), reservation.nombre_personnes)
            )
            events.append(
                (min(reservation_end, candidate_end), -reservation.nombre_personnes)
            )

    occupancy = 0
    for moment in sorted({event_time for event_time, _ in events}):
        occupancy += sum(delta for event_time, delta in events if event_time == moment)
        if occupancy + party_size > config.capacity:
            return False
    return party_size <= config.capacity


def generate_available_slots(day, party_size, *, now=None):
    return [
        slot
        for slot in generate_candidate_slots(day, party_size, now=now)
        if is_slot_available(day, slot, party_size)
    ]
