from datetime import date

from .models import SpecialOpeningHours, WeeklyOpeningHours


def get_effective_intervals(day: date):
    special = SpecialOpeningHours.objects.filter(date=day).first()
    if special:
        if special.closed:
            return []
        return [(special.opens_at, special.closes_at)]

    return list(
        WeeklyOpeningHours.objects.filter(weekday=day.weekday())
        .order_by("opens_at")
        .values_list("opens_at", "closes_at")
    )


def format_time(value):
    return value.strftime("%Hh%M")


def get_opening_summary(day: date):
    special = SpecialOpeningHours.objects.filter(date=day).first()
    if special and special.closed:
        suffix = f" — {special.description}" if special.description else ""
        return f"Fermé exceptionnellement{suffix}"

    intervals = get_effective_intervals(day)
    if not intervals:
        return "Fermé"
    return " / ".join(
        f"{format_time(opens_at)}–{format_time(closes_at)}"
        for opens_at, closes_at in intervals
    )


def get_weekly_schedule():
    schedule = []
    for weekday, label in WeeklyOpeningHours.WEEKDAYS:
        intervals = list(
            WeeklyOpeningHours.objects.filter(weekday=weekday)
            .order_by("opens_at")
            .values_list("opens_at", "closes_at")
        )
        summary = "Fermé"
        if intervals:
            summary = " / ".join(
                f"{format_time(opens_at)}–{format_time(closes_at)}"
                for opens_at, closes_at in intervals
            )
        schedule.append(
            {"weekday": weekday, "label": label, "summary": summary}
        )
    return schedule
