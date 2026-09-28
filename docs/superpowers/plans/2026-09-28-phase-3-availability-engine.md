# Phase 3 — Reservation availability and capacity

## Goal

Provide one server-side availability engine that generates bookable arrival
times from restaurant hours and rejects reservations that would exceed the
configured simultaneous capacity.

## Task 1 — Slot generation

Files:

- `reservations/services/availability.py`
- `reservations/tests/test_availability.py`

Steps:

1. Test 30-minute slot generation for lunch and dinner services.
2. Test exceptional closure and exceptional opening precedence.
3. Test past dates, the minimum booking delay, and party-size limits.
4. Implement generation using the `restaurant` domain services and settings.

## Task 2 — Capacity calculation

Files:

- `reservations/services/availability.py`
- `reservations/tests/test_availability.py`

Steps:

1. Test overlapping reservations at the start, middle, and end of a 90-minute
   stay.
2. Test exact capacity, exceeded capacity, and non-overlapping reservations.
3. Implement capacity checks using timezone-aware datetimes.

## Task 3 — Transactional creation and public endpoint

Files:

- `reservations/models.py`
- `reservations/migrations/0003_*.py`
- `reservations/services/booking.py`
- `reservations/views.py`
- `reservations/urls.py`
- `reservations/tests/test_booking.py`

Steps:

1. Add a per-date lock model and failing transactional booking tests.
2. Revalidate opening hours, party-size rules, and capacity inside an atomic
   transaction before saving.
3. Add a read-only JSON endpoint returning available times for a date and party
   size, with explicit validation errors.
4. Keep the existing reservation page functional; the three-step UI is handled
   in the next reservation-lifecycle phase.

## Verification

- targeted availability and booking tests
- full Django test suite
- `manage.py check`
- `makemigrations --check --dry-run`
- copied database migration
- diff review and separate commits per task
