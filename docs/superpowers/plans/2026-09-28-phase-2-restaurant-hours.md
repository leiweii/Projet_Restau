# Phase 2 — Restaurant information and opening hours

## Goal

Create one database-backed source for Restaurant Osaka's public information,
reservation limits, weekly services, and exceptional opening hours. Preserve the
existing reservation and special-hours data while removing hard-coded public
opening hours.

## Task 1 — Create the `restaurant` domain

Files:

- `restaurant/models.py`
- `restaurant/admin.py`
- `restaurant/apps.py`
- `restaurant/tests/test_models.py`
- `restaurant_project/settings/base.py`
- generated migration

Steps:

1. Add failing tests for the singleton configuration defaults and weekly interval
   validation.
2. Create `RestaurantSettings` with public identity/contact fields and the
   approved defaults: 20 covers, 90 minutes, 30-minute interval, 2-hour cutoff,
   and 8-person online limit.
3. Create `WeeklyOpeningHours`, supporting multiple services per weekday and
   rejecting end times before start times or overlapping services.
4. Register both models in Django Admin and generate the migration.
5. Run targeted and full tests, then commit.

## Task 2 — Move exceptional hours into the domain

Files:

- `restaurant/models.py`
- `restaurant/migrations/0002_*.py`
- `restaurant/tests/test_migrations.py`
- `reservations/models.py`
- `reservations/forms.py`
- `reservations/admin.py`
- `core/views.py`

Steps:

1. Add a failing migration test using representative existing `HoraireSpecial`
   records.
2. Add `SpecialOpeningHours` and a data migration that copies all existing rows.
3. Switch current imports, forms, admin, and views to the new model without
   deleting the legacy table in this phase.
4. Verify copied database data and commit.

## Task 3 — Seed and expose real opening information

Files:

- `restaurant/services.py`
- `restaurant/management/commands/seed_restaurant.py`
- `restaurant/tests/test_services.py`
- `core/views.py`
- `core/templates/core/home.html`
- `core/templates/core/contact.html`

Steps:

1. Add failing service tests for weekly hours, exceptional closure precedence,
   and today's opening summary.
2. Implement query services used by public pages and the future availability
   engine.
3. Add an idempotent seed command for the existing displayed schedule and safe
   placeholder public contact information.
4. Replace the hard-coded contact schedule and expose the same source on home.
5. Run targeted tests, full tests, migration drift checks, and visual smoke
   checks; commit.

## Verification

- `python manage.py test`
- `python manage.py check`
- `python manage.py makemigrations --check --dry-run`
- migrate a copy of the existing SQLite database
- inspect mobile and desktop versions of `/` and `/contact/`
- review `main...HEAD` for unrelated or destructive changes

The existing Gmail credential remains revoked outside the code. This phase does
not add ordering, payment, delivery, physical table assignment, or invented
restaurant contact details.
