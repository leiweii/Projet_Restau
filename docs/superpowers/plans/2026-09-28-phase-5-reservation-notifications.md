# Reservation Notifications Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make reservation confirmation independent from email delivery while sending the guest a secure management link and notifying the restaurant.

**Architecture:** Move message construction and delivery out of the view into a focused notification service. The booking view commits the reservation first, then invokes the service; delivery errors are logged with the reservation identifier and the confirmation page remains successful.

**Tech Stack:** Django 5.1, Django email API, server-rendered templates, Python logging, Django TestCase.

**Spec:** `docs/superpowers/specs/2026-09-27-restaurant-osaka-design.md`

## Global Constraints

- Reservation creation must succeed independently of SMTP delivery.
- The client email contains the reservation summary and secure management URL.
- SMTP errors are logged without personal contact details.
- Existing reservation, account, and availability behavior remains unchanged.
- No background queue or new dependency is introduced in this phase.

## Review Focus

- Client delivery failure must not skip the restaurant notification attempt.
- Restaurant delivery failure must not duplicate or roll back the reservation.
- The management URL must be absolute and contain only the reservation token.
- Logs must identify the reservation without storing email, phone, or message bodies.
- Development and test email backends must remain usable without credentials.

---

### Task 1: Notification service

**Files:**
- Create: `reservations/services/notifications.py`
- Create: `reservations/tests/test_notifications.py`

**Interfaces:**
- Consumes: `Reservation`, `request.build_absolute_uri()`, Django `send_mail`.
- Produces: `send_reservation_notifications(reservation, request) -> NotificationResult` with separate client and restaurant delivery booleans.

- [ ] Write failing tests proving both messages contain the correct information, the client email contains the absolute management URL, one failed recipient does not prevent the other attempt, and failures log only the reservation id.
- [ ] Run `manage.py test reservations.tests.test_notifications` and verify failure because the service does not exist.
- [ ] Implement the notification service with one guarded delivery attempt per recipient.
- [ ] Re-run the targeted tests and expect all to pass.
- [ ] Commit with `feat: make reservation notifications fault tolerant`.

### Task 2: Booking view integration

**Files:**
- Modify: `reservations/views.py`
- Modify: `reservations/tests/test_reservations.py`

**Interfaces:**
- Consumes: `send_reservation_notifications(reservation, request)` from Task 1.
- Produces: successful confirmation response after database creation regardless of notification result.

- [ ] Write failing integration tests proving an SMTP exception still returns the confirmation and creates exactly one reservation, and a normal request sends two messages.
- [ ] Run `manage.py test reservations.tests.test_reservations` and verify the SMTP failure test fails against the current view.
- [ ] Replace inline email delivery in the view with the notification service.
- [ ] Re-run targeted tests and expect all to pass.
- [ ] Run the full suite, Django checks, migration drift check, and diff check.
- [ ] Commit with `refactor: decouple booking from email delivery`.
