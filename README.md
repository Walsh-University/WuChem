# WuChem

WuChem is a mobile-first web application for university chemistry labs. It is being built to give students and faculty quick access to chemical safety information while giving lab staff practical tools for inventory and compliance work.

The main workflow starts with a barcode. A student or faculty member scans a chemical container with a phone or handheld scanner, then uses WuChem to find the chemical record, Safety Data Sheet (SDS), hazards, storage information, and disposal guidance.

This repository is still in its early stages. It began as a copy of an existing LIMS project, and the inherited LIMS features are being removed or replaced as WuChem takes shape.

## Current state

The application currently has:

- A responsive dashboard designed for phones first
- Barcode and chemical search entry points
- Student, Faculty, and Admin roles
- Role-aware dashboard content and navigation
- Django admin access for Admin users
- Local username/password authentication
- PostgreSQL configuration for development and production
- Health and readiness endpoints
- A Bootstrap-based theme using the university maroon and gold palette

Chemical records, SDS document storage, live inventory counts, disposal requests, alerts, and camera-based barcode scanning have not been implemented yet. The dashboard shows empty states where those features will connect later; it does not use made-up production data.

## Roles

WuChem has one shared interface with capabilities added according to a user's role.

| Capability | Student | Faculty | Admin |
| --- | :---: | :---: | :---: |
| Search or scan chemicals | Yes | Yes | Yes |
| View SDS and safety guidance | Yes | Yes | Yes |
| View disposal and emergency information | Yes | Yes | Yes |
| View inventory status and alerts | No | Yes | Yes |
| Manage inventory | No | Yes | Yes |
| Manage users and application settings | No | No | Yes |

Roles are stored on the user account and synchronized with reserved Django groups. Individual permissions can be added as the system grows, so future roles such as Lab Manager, Safety Officer, or Stockroom Technician do not require a separate application.

## Technology

- Python 3.14+
- Django 6.1
- PostgreSQL
- Django templates
- Bootstrap 5 with project SCSS overrides
- HTMX and Alpine.js, available for later interactive workflows
- `uv` for Python dependencies and commands
- pytest, pytest-django, Ruff, and coverage.py for quality checks

## Local setup

### Requirements

Install the following before starting:

- Python 3.14 or a compatible `uv`-managed Python
- [`uv`](https://docs.astral.sh/uv/)
- PostgreSQL
- Sass only if you plan to change the styles

### Install dependencies

```bash
uv sync --group dev
```

### Configure the database

WuChem reads a standard `DATABASE_URL`. For example:

```bash
export DATABASE_URL="postgresql://wuchem:password@localhost:5432/wuchem"
```

You can also use the individual `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT` variables. See `config/settings/base.py` for the current defaults and all supported settings.

For local development, set a Django secret and enable debug output:

```bash
export DJANGO_SECRET_KEY="replace-this-for-local-development"
export DJANGO_DEBUG=1
```

### Initialize the application

```bash
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

Open <http://127.0.0.1:8000/>. The first superuser has full Django permissions; users created through the admin can be assigned the Student, Faculty, or Admin role.

## Development commands

Run the test suite without the repository-wide coverage gate:

```bash
DJANGO_SETTINGS_MODULE=config.settings.test uv run pytest --no-cov
```

Run linting and formatting checks:

```bash
uv run ruff check accounts chem_core config tests
uv run ruff format --check accounts chem_core config tests
```

Rebuild the application and Django admin styles:

```bash
make css
```

Check Django configuration and migration state:

```bash
DJANGO_SETTINGS_MODULE=config.settings.test uv run python manage.py check
DJANGO_SETTINGS_MODULE=config.settings.test uv run python manage.py makemigrations --check --dry-run
```

## Project layout

```text
accounts/       Custom user model, roles, groups, and admin integration
chem_core/      Dashboard, search, status checks, URLs, and shared templates
config/         Django settings, root URLs, logging, ASGI, and WSGI
assets/scss/    Bootstrap source and WuChem theme overrides
static/         Compiled CSS and browser JavaScript
templates/      Login and Django admin templates
tests/          Role, permission, authentication, and dashboard tests
```

## Authentication

Local development uses Django's username and password authentication. The settings include preliminary SAML configuration for Microsoft Entra, inherited from the earlier project, but the WuChem account model and SAML integration have not been completed or tested together. Keep `SAML_ENABLED=0` until that work is finished.

## Safety and compliance

WuChem is intended to help people find laboratory safety information quickly. It does not replace an SDS, the university's chemical hygiene plan, emergency procedures, required training, or guidance from the institution's Environmental Health and Safety staff.

Hazard summaries and disposal instructions should be treated as controlled content. Before these features are released, the project will need an ownership and review process for source documents, revisions, approvals, and audit history.

## Near-term work

The next useful slice is the chemical record itself:

1. Define chemicals, products, containers, storage locations, and barcodes.
2. Store SDS metadata and controlled document revisions.
3. Return a useful chemical detail page after barcode lookup.
4. Add inventory quantities and low-stock rules for Faculty and Admin users.
5. Add disposal requests, safety notices, and audit history.

Camera scanning can be added after the barcode lookup contract is stable. USB and Bluetooth handheld scanners can already work as keyboard input through the dashboard search field.
