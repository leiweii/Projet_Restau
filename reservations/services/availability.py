from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone

from restaurant.models import RestaurantSettings
from restaurant.services import get_effective_intervals


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
