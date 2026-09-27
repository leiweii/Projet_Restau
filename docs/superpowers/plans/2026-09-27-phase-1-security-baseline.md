# Phase 1 Security Baseline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove committed runtime secrets from active configuration, separate development and production settings, minimize request logging, clean generated files from the Git index, and restore a migration-clean tested baseline.

**Architecture:** Replace the single settings module with a settings package containing shared, development, and production modules. Keep configuration parsing in a small standard-library helper, keep development safe from accidental SMTP sends, and make production fail fast when required environment variables are absent. Treat logging hygiene and the existing menu migration drift as separate reviewable changes.

**Tech Stack:** Python 3, Django 5.1.7, SQLite for local verification, PowerShell commands on Windows, Django `TestCase` and `SimpleTestCase`.

**Spec:** `docs/superpowers/specs/2026-09-27-restaurant-osaka-design.md`

## Global Constraints

- Preserve all existing accounts, dishes, images, promotions, and reservations.
- Keep the application a server-rendered modular Django monolith; do not add React, DRF, microservices, ordering, delivery, or payment.
- Use `Europe/Paris` for application time.
- Use only Python standard-library environment parsing in this phase; add no configuration dependency.
- Never print, copy, or reuse the committed Gmail application password.
- The user must revoke the exposed Gmail application password in Google; code changes cannot revoke it.
- Do not delete local log or coverage files. Remove generated files from the Git index while leaving working-tree copies intact.
- Keep each task in its own commit and run its targeted tests before the full suite.
- Do not change authentication behavior, reservation models, or reservation migrations in this phase.

## Review Focus

- A missing required production secret must stop startup with a named configuration error, never fall back to the development key; pinned by Task 1 production-settings tests.
- Boolean text such as `false`, `0`, and `off` must not become truthy merely because it is a non-empty string; pinned by Task 1 environment-helper tests.
- A request log must not contain the authenticated username, email, forwarded IP, or remote IP; pinned by Task 2 middleware tests.
- Removing tracked logs and coverage data must leave the local files present and ignored; pinned by Task 2 Git verification steps.
- Two promotional menus with the same name must be rejected consistently by both model metadata and the database; pinned by Task 3 model and migration tests.

---

## File Map

### Settings boundary

- Delete: `restaurant_project/settings.py`
- Create: `restaurant_project/settings/__init__.py` — settings-package marker with no environment selection.
- Create: `restaurant_project/settings/env.py` — `env_value`, `env_bool`, and `env_list` parsing helpers.
- Create: `restaurant_project/settings/base.py` — installed apps, middleware, templates, database, locale, static/media, authentication redirects, and console logging shared by all environments.
- Create: `restaurant_project/settings/development.py` — development key, `DEBUG=True`, local hosts, console email backend.
- Create: `restaurant_project/settings/production.py` — required secrets and hosts, SMTP settings, HTTPS/cookie protections, production logging.
- Modify: `manage.py` — default to development settings.
- Modify: `restaurant_project/asgi.py` — default to production settings.
- Modify: `restaurant_project/wsgi.py` — default to production settings.
- Create: `restaurant_project/tests/__init__.py` — project-level test package.
- Create: `restaurant_project/tests/test_settings.py` — isolated environment-parser and settings-import tests.

### Logging and repository hygiene

- Modify: `accounts/middleware.py` — log method, path, status, and duration only.
- Create: `accounts/tests_logging.py` — middleware privacy tests without restructuring the existing `accounts/tests.py` module.
- Modify: `.gitignore` — ignore environment files, logs, coverage data, backups, caches, and local databases while retaining `.env.example`.
- Untrack, preserving local files: `.coverage`, `logs/*.log`.

### Migration consistency

- Modify: `menu/models.py` — use the Boolean `unique=True` declaration for `MenuPromotionnel.nom`.
- Create: `menu/migrations/0005_alter_menupromotionnel_nom.py` — align the database constraint with the model.
- Modify: `menu/tests.py` — test model metadata and duplicate-name rejection.

### Operator documentation

- Create: `.env.example` — names and safe placeholder values for production variables.
- Modify: `README.md` — correct setup commands, settings selection, secret handling, test commands, implemented-vs-planned status, and password-revocation warning.

---

### Task 1: Separate Development and Production Settings

**Files:**

- Delete: `restaurant_project/settings.py`
- Create: `restaurant_project/settings/__init__.py`
- Create: `restaurant_project/settings/env.py`
- Create: `restaurant_project/settings/base.py`
- Create: `restaurant_project/settings/development.py`
- Create: `restaurant_project/settings/production.py`
- Modify: `manage.py:7-18`
- Modify: `restaurant_project/asgi.py:10-16`
- Modify: `restaurant_project/wsgi.py:10-16`
- Create: `restaurant_project/tests/__init__.py`
- Create: `restaurant_project/tests/test_settings.py`

**Interfaces:**

- Produces: `env_value(name: str, default: str | None = None, *, required: bool = False) -> str` in `restaurant_project.settings.env`.
- Produces: `env_bool(name: str, default: bool = False) -> bool` accepting case-insensitive `1,true,yes,on` and `0,false,no,off`, raising `django.core.exceptions.ImproperlyConfigured` for other values.
- Produces: `env_list(name: str, default: tuple[str, ...] = ()) -> list[str]`, parsing comma-separated non-empty values with surrounding whitespace removed.
- Produces: `restaurant_project.settings.development` as the default settings module for `manage.py`.
- Produces: `restaurant_project.settings.production` as the default settings module for ASGI and WSGI.
- Produces: required production variables `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `PATRON_EMAIL`, and `DEFAULT_FROM_EMAIL`.
- Produces: optional production variables `EMAIL_HOST` (default `smtp.gmail.com`), `EMAIL_PORT` (default `587`), and `EMAIL_USE_TLS` (default `true`).
- Consumes: existing settings behavior from `restaurant_project/settings.py`, except secrets, UTC timezone, file logging, and live SMTP defaults.

- [ ] **Step 1: Write failing environment-helper tests**

Add `EnvironmentHelperTests` in `restaurant_project/tests/test_settings.py` with these assertions:

```python
def test_required_value_names_missing_variable(self):
    with patch.dict(os.environ, {}, clear=True):
        with self.assertRaisesMessage(ImproperlyConfigured, "DJANGO_SECRET_KEY"):
            env_value("DJANGO_SECRET_KEY", required=True)

def test_boolean_false_values_are_false(self):
    for value in ("0", "false", "no", "off", "FALSE"):
        with self.subTest(value=value), patch.dict(os.environ, {"FLAG": value}):
            self.assertIs(env_bool("FLAG", default=True), False)

def test_list_removes_whitespace_and_empty_items(self):
    with patch.dict(os.environ, {"HOSTS": " osaka.fr, www.osaka.fr, "}):
        self.assertEqual(env_list("HOSTS"), ["osaka.fr", "www.osaka.fr"])
```

- [ ] **Step 2: Run the helper tests and verify the expected failure**

Run: `.\env\Scripts\python.exe manage.py test restaurant_project.tests.test_settings.EnvironmentHelperTests --settings=restaurant_project.settings --verbosity 2`

Expected: FAIL because `restaurant_project.settings.env` and its functions do not exist.

- [ ] **Step 3: Create the settings package and environment helpers**

Replace `settings.py` with the mapped package. Implement the exact helper signatures from Interfaces. In `base.py`, calculate the project root with `BASE_DIR = Path(__file__).resolve().parents[2]`, move the common settings there, set `TIME_ZONE = "Europe/Paris"`, and configure console-only logging without creating a `logs` directory at import time.

- [ ] **Step 4: Configure development and production modules**

In `development.py`, import from `base`, use a documented development-only secret, set `DEBUG=True`, allow `localhost`, `127.0.0.1`, and `[::1]`, and use `django.core.mail.backends.console.EmailBackend`.

In `production.py`, require `DJANGO_SECRET_KEY` and at least one `DJANGO_ALLOWED_HOSTS` value; set `DEBUG=False`, `SECURE_SSL_REDIRECT=True`, `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`, `SECURE_HSTS_SECONDS=31536000`, `SECURE_HSTS_INCLUDE_SUBDOMAINS=True`, `SECURE_HSTS_PRELOAD=True`, and `SECURE_REFERRER_POLICY="same-origin"`. Configure SMTP only from the environment variables named in Interfaces.

- [ ] **Step 5: Point each entry point at the correct environment**

Set `manage.py` to `restaurant_project.settings.development`. Set `asgi.py` and `wsgi.py` to `restaurant_project.settings.production`. Preserve explicit `DJANGO_SETTINGS_MODULE` values supplied by callers through `setdefault`.

- [ ] **Step 6: Add isolated production-settings tests**

In `test_settings.py`, use `subprocess.run([sys.executable, "-c", script], env=clean_env, ...)` so production imports do not pollute Django's active settings. Test:

```python
def test_production_requires_secret_key(): ...
def test_production_requires_allowed_hosts(): ...
def test_production_enables_https_and_secure_cookies(): ...
def test_development_uses_console_email_backend(): ...
def test_development_uses_europe_paris_timezone(): ...
```

The successful production subprocess supplies safe test-only values and asserts `DEBUG is False`, parsed hosts equal `['example.com']`, and all specified security flags are enabled.

- [ ] **Step 7: Run targeted settings tests**

Run: `.\env\Scripts\python.exe manage.py test restaurant_project.tests.test_settings --verbosity 2`

Expected: all settings tests PASS.

- [ ] **Step 8: Run Django checks and the existing suite**

Run: `.\env\Scripts\python.exe manage.py check`

Expected: `System check identified no issues`.

Run: `.\env\Scripts\python.exe manage.py test --verbosity 1`

Expected: all existing and new tests PASS.

- [ ] **Step 9: Commit the settings boundary**

```powershell
git add -- manage.py restaurant_project/asgi.py restaurant_project/wsgi.py restaurant_project/settings restaurant_project/tests
git add -u -- restaurant_project/settings.py
git commit -m "refactor: separate development and production settings"
```

### Task 2: Minimize Request Logging and Untrack Generated Artifacts

**Files:**

- Modify: `accounts/middleware.py:1-56`
- Create: `accounts/tests_logging.py`
- Modify: `.gitignore`
- Untrack while preserving locally: `.coverage`, `logs/requests_2025-04-09.log`, `logs/requests_2025-04-10.log`, `logs/requests_2025-04-15.log`, `logs/requests_2025-04-17.log`, `logs/requests_2025-04-24.log`, `logs/requests_2025-09-25.log`, `logs/requests_2026-02-08.log`

**Interfaces:**

- Consumes: `RequestLoggingMiddleware(get_response)` as configured in base settings.
- Produces: one completion log record per request with `method`, `path`, `status_code`, and integer `duration_ms`.
- Produces: error log level for status codes `>= 400`, info otherwise.
- Produces: ignore rules for `.env`, `.env.*` except `.env.example`, `logs/`, `.coverage`, `htmlcov/`, `.backups/`, `*.sqlite3`, caches, and the existing virtual environment/media/static rules.

- [ ] **Step 1: Write failing middleware privacy tests**

In `accounts/tests_logging.py`, create `RequestLoggingMiddlewareTests` using `RequestFactory`, an authenticated user with email, `REMOTE_ADDR="192.0.2.1"`, and `HTTP_X_FORWARDED_FOR="198.51.100.2"`.

Add tests with these assertions:

```python
def test_success_log_contains_operational_fields_only(self):
    self.assertIn("GET", message)
    self.assertIn("/menu/", message)
    self.assertIn("200", message)
    self.assertNotIn(self.user.username, message)
    self.assertNotIn(self.user.email, message)
    self.assertNotIn("192.0.2.1", message)
    self.assertNotIn("198.51.100.2", message)

def test_error_response_uses_error_level(self):
    self.assertEqual(captured.records[-1].levelname, "ERROR")

def test_middleware_emits_one_record_per_request(self):
    self.assertEqual(len(captured.records), 1)
```

- [ ] **Step 2: Run logging tests and verify they fail**

Run: `.\env\Scripts\python.exe manage.py test accounts.tests_logging --verbosity 2`

Expected: FAIL because the current middleware logs username and IP address and emits two records.

- [ ] **Step 3: Implement minimal privacy-conscious logging**

Remove `json`, `get_client_ip`, the request-start log, username, and IP collection. Emit one structured-format message after the response using the fields in Interfaces. Preserve exception propagation; do not swallow application exceptions.

- [ ] **Step 4: Run logging tests**

Run: `.\env\Scripts\python.exe manage.py test accounts.tests_logging --verbosity 2`

Expected: all middleware logging tests PASS.

- [ ] **Step 5: Extend `.gitignore` without deleting files**

Add the exact generated/local patterns from Interfaces. Keep `!.env.example` after `.env.*`. Do not ignore source migrations, uploaded fixture examples, or documentation.

- [ ] **Step 6: Remove generated artifacts from the index only**

Run:

```powershell
git rm --cached -- .coverage
git rm -r --cached -- logs
```

Expected: Git stages deletions, while `Test-Path .coverage` and `Test-Path logs/requests_2025-04-09.log` both return `True`.

- [ ] **Step 7: Verify exact ignore behavior and staged scope**

Run:

```powershell
git check-ignore -v .coverage htmlcov/index.html logs/requests_2026-09-27.log .env .backups/db.sqlite3
git status --short --untracked-files=all
git diff --cached --name-status
```

Expected: all generated examples are ignored; staged deletions are limited to the tracked coverage/log artifacts; source files are not ignored.

- [ ] **Step 8: Run targeted and full tests**

Run: `.\env\Scripts\python.exe manage.py test accounts.tests_logging --verbosity 2`

Run: `.\env\Scripts\python.exe manage.py test --verbosity 1`

Expected: both commands PASS.

- [ ] **Step 9: Commit logging and repository hygiene**

```powershell
git add -- .gitignore accounts/middleware.py accounts/tests_logging.py
git commit -m "chore: minimize request logs and ignore local artifacts"
```

### Task 3: Resolve Promotional Menu Migration Drift

**Files:**

- Modify: `menu/models.py:34-41`
- Create: `menu/migrations/0005_alter_menupromotionnel_nom.py`
- Modify: `menu/tests.py`

**Interfaces:**

- Consumes: existing `MenuPromotionnel(nom, plat_principal, plat_associe)` model.
- Produces: `MenuPromotionnel.nom` with `unique=True` as a Boolean model option and a matching database uniqueness constraint.
- Produces: migration dependency on `menu.0004_menupromotionnel`.

- [ ] **Step 1: Back up the local database before migration work**

Run:

```powershell
New-Item -ItemType Directory -Force .backups | Out-Null
Copy-Item -LiteralPath db.sqlite3 -Destination .backups/db-before-phase-1.sqlite3
```

Expected: both database files exist, and `.backups/db-before-phase-1.sqlite3` is ignored by Git.

- [ ] **Step 2: Write failing model tests**

Add `MenuPromotionnelConstraintTests` in `menu/tests.py`. Its setup creates one category and two dishes. Add:

```python
def test_nom_unique_metadata_is_boolean_true(self):
    field = MenuPromotionnel._meta.get_field("nom")
    self.assertIs(field.unique, True)

def test_duplicate_nom_is_rejected_by_database(self):
    MenuPromotionnel.objects.create(nom="Menu Osaka", ...)
    with self.assertRaises(IntegrityError):
        with transaction.atomic():
            MenuPromotionnel.objects.create(nom="Menu Osaka", ...)
```

- [ ] **Step 3: Run the constraint tests and verify failure**

Run: `.\env\Scripts\python.exe manage.py test menu.tests.MenuPromotionnelConstraintTests --verbosity 2`

Expected: at least the database-constraint test FAILS because migration `0004` does not create a unique constraint.

- [ ] **Step 4: Correct the model declaration and generate the migration**

Change the declaration to `nom = models.CharField(max_length=100, unique=True)`.

Run: `.\env\Scripts\python.exe manage.py makemigrations menu`

Expected: create only `menu/migrations/0005_alter_menupromotionnel_nom.py` with an `AlterField` operation.

- [ ] **Step 5: Inspect existing data before applying the unique constraint**

Run a read-only Django shell query grouping `MenuPromotionnel` by `nom` and printing only duplicate names and counts, never unrelated customer data.

Expected: no duplicates. If duplicates exist, stop and ask the user which record should retain the name; do not rename or delete automatically.

- [ ] **Step 6: Apply and verify the migration**

Run: `.\env\Scripts\python.exe manage.py migrate menu`

Expected: migration `menu.0005...` applies successfully.

Run: `.\env\Scripts\python.exe manage.py makemigrations --check --dry-run`

Expected: `No changes detected`.

- [ ] **Step 7: Run targeted and full tests**

Run: `.\env\Scripts\python.exe manage.py test menu.tests.MenuPromotionnelConstraintTests --verbosity 2`

Run: `.\env\Scripts\python.exe manage.py test --verbosity 1`

Expected: both commands PASS.

- [ ] **Step 8: Commit the migration consistency fix**

```powershell
git add -- menu/models.py menu/migrations/0005_alter_menupromotionnel_nom.py menu/tests.py
git commit -m "fix: align promotional menu uniqueness migration"
```

### Task 4: Document Safe Setup and Verify the Baseline

**Files:**

- Create: `.env.example`
- Modify: `README.md`

**Interfaces:**

- Consumes: settings modules and production variable names from Task 1.
- Produces: copyable Windows and Unix setup commands that use the actual `env` directory name.
- Produces: documented development command using default development settings.
- Produces: documented production variable contract without real credentials.
- Produces: accurate `Implemented`, `Planned`, and `Security notice` sections.

- [ ] **Step 1: Create `.env.example` with placeholders only**

List these names with non-secret placeholders or empty values:

```dotenv
DJANGO_SECRET_KEY=replace-with-a-long-random-production-secret
DJANGO_ALLOWED_HOSTS=example.com,www.example.com
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
PATRON_EMAIL=
DEFAULT_FROM_EMAIL=Restaurant Osaka <noreply@example.com>
```

Do not add the old Gmail username, password, personal recipient address, or Django key.

- [ ] **Step 2: Rewrite setup and status sections in README**

Correct the virtual-environment activation commands to use `env`, install from `requirements.txt`, document migrations/tests, and distinguish existing features from the approved roadmap. Add a prominent instruction that the previously committed Gmail application password must be revoked in Google and replaced through environment configuration.

- [ ] **Step 3: Scan tracked source for the exposed secret classes**

Run focused searches for `EMAIL_HOST_PASSWORD =`, `django-insecure-`, and the old SMTP credential value in tracked files. Do not print matching secret values to the conversation.

Expected: active tracked source contains no real credential; the README may contain only generic variable names and safe examples.

- [ ] **Step 4: Run the complete verification matrix**

Run:

```powershell
.\env\Scripts\python.exe manage.py check
.\env\Scripts\python.exe manage.py makemigrations --check --dry-run
.\env\Scripts\python.exe manage.py test --verbosity 1
```

Expected: system check clean, no pending migrations, all tests PASS.

Run the production deployment check with safe, process-local test values:

```powershell
$env:DJANGO_SECRET_KEY='test-only-secret-with-more-than-fifty-random-looking-characters-12345'
$env:DJANGO_ALLOWED_HOSTS='example.com'
$env:EMAIL_HOST_USER='test@example.com'
$env:EMAIL_HOST_PASSWORD='test-only-password'
$env:PATRON_EMAIL='owner@example.com'
$env:DEFAULT_FROM_EMAIL='Restaurant Osaka <noreply@example.com>'
.\env\Scripts\python.exe manage.py check --deploy --settings=restaurant_project.settings.production
```

Expected: no Django deployment warnings caused by settings controlled in this phase. Remove the process-local test variables after the command.

- [ ] **Step 5: Inspect the final phase diff and repository state**

Run:

```powershell
git diff --check
git status --short --branch
git log --oneline -5
```

Expected: only `.env.example` and `README.md` remain for this task; prior tasks appear as separate commits; local logs, coverage data, database, backup, and virtual environment do not appear as untracked files.

- [ ] **Step 6: Commit operator documentation**

```powershell
git add -- .env.example README.md
git commit -m "docs: document secure local and production setup"
```

- [ ] **Step 7: Record the manual security prerequisite in the handoff**

Report that the code no longer uses committed secrets, but do not claim the exposed Gmail application password is revoked until the user confirms completing that Google-account action.

---

## Phase Completion Criteria

Phase 1 is complete only when:

- settings tests and the full Django suite pass;
- development sends email to the console rather than Gmail;
- production settings fail fast without required environment variables;
- `check --deploy` is clean for the configured production settings;
- `makemigrations --check --dry-run` reports no changes;
- generated logs and coverage artifacts remain locally available but are not tracked;
- the promotional-menu uniqueness constraint exists in both model state and database schema;
- README and `.env.example` contain no real secret;
- commits remain separated by task;
- the user is explicitly reminded to revoke the old Gmail application password.

After this phase is reviewed, create the next plan for unified restaurant information and weekly/special opening hours. Do not begin reservation-capacity implementation in Phase 1.
