# Phase 4 — Reservation lifecycle and guest management

## Goal

Replace destructive reservation deletion with a traceable lifecycle, enforce the
two-hour modification/cancellation cutoff, and let guests manage a reservation
through a private, unguessable link.

## Tasks

1. Add reservation statuses, a UUID management token, and update timestamps.
   Preserve all existing reservations as confirmed through a migration.
2. Make capacity calculations ignore cancelled, completed, and no-show records.
3. Add transactional modification and cancellation services. Both must lock the
   reservation day and enforce the configured cutoff; modification must recheck
   opening hours and capacity while excluding the current reservation.
4. Reuse the same lifecycle services for signed-in customers and guest token
   pages. Display the management link after a guest booking.
5. Update staff actions to cancel instead of delete, then run targeted tests,
   the complete suite, migration checks, and Django system checks.

## Boundaries

- No email delivery redesign in this phase.
- No payment or online ordering.
- No historical reservation is deleted.
- Staff may cancel a reservation even after the customer cutoff; customer and
  guest actions remain constrained by the cutoff.
