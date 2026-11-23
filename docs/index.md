# Developer onboarding

Welcome to WuChem. This guide takes a new developer from a fresh checkout to a
working local environment, then points to the parts of the codebase they are
most likely to change.

WuChem is a mobile-first Django application for finding chemical records,
Safety Data Sheets (SDS), storage guidance, and inventory information. The
project is still evolving, so treat the models, tests, and configuration as the
source of truth when older descriptions disagree with the code.

## What you need

- Git
- [`uv`](https://docs.astral.sh/uv/) for Python and dependency management
- Docker with Docker Compose, or a local PostgreSQL server
- Sass only when changing files under `assets/scss/`

The project requires Python 3.14 or newer. `uv` can install and select a
compatible interpreter for you.

## First-time setup

### 1. Install the project dependencies

From the repository root, run:

```bash
uv python install 3.14
uv sync --group dev
```

`uv sync` creates or updates the local virtual environment and installs the
locked application and development dependencies.

### 2. Configure the local environment

Copy the example environment file, then keep the resulting `.env` file local:

```bash
cp .env-example .env
```

At minimum, set these database values in `.env`:

```dotenv
DB_NAME=wuchem
DB_USER=wuchem
DB_PASSWORD=wuchem_dev_password
DB_HOST=localhost
DB_PORT=5432
```

The development settings load `.env` automatically. The checked-in example
also supplies safe local values for the Django settings module, debug mode,
allowed hosts, and the public URL. Do not commit secrets or your local `.env`.

Single sign-on is not required for local development. Local username/password
authentication is the supported development path; leave SAML disabled unless
you are actively working on that integration.

### 3. Start PostgreSQL

To use the included PostgreSQL container:

```bash
docker compose --env-file .env -f docker/docker-compose.yml up -d db
```

If PostgreSQL is already running on your machine, create the database and user
that match `.env` instead. The application also accepts a single
`DATABASE_URL` in place of the individual `DB_*` values.

### 4. Initialize and run Django

```bash
uv run python manage.py migrate
uv run python manage.py createsuperuser
uv run python manage.py runserver
```

Open <http://127.0.0.1:8000/> and sign in with the superuser you created. The
Django administration site is at <http://127.0.0.1:8000/admin/>.

To stop the database container later, run:

```bash
docker compose --env-file .env -f docker/docker-compose.yml stop db
```

## Verify your setup

Run the same core checks used by continuous integration:

```bash
uv run ruff check .
uv run ruff format --check .
uv run ty check .
uv run pytest
```

The test settings use an in-memory SQLite database, so the test suite does not
need the PostgreSQL container. The default pytest configuration enforces at
least 80% coverage.

For a faster local test run without the repository-wide coverage gate:

```bash
uv run pytest --no-cov
```

You can also verify Django configuration and migration state directly:

```bash
DJANGO_SETTINGS_MODULE=config.settings.test uv run python manage.py check
DJANGO_SETTINGS_MODULE=config.settings.test uv run python manage.py makemigrations --check --dry-run
```

## Codebase tour

| Path | Responsibility |
| --- | --- |
| `accounts/` | Custom user model, Student/Faculty/Admin roles, reserved groups, and admin integration |
| `inventory/` | Chemicals, products, SDS links, storage locations, search, and chemical detail pages |
| `chem_core/` | Dashboard, shared UI, application status, and top-level search entry point |
| `config/` | Settings, root URL routing, logging, observability, ASGI, and WSGI |
| `templates/` | Project-level login and Django admin template overrides |
| `assets/scss/` | Bootstrap source and WuChem theme overrides |
| `static/` | Compiled CSS and browser JavaScript |
| `tests/` | Application, permission, inventory, observability, and status tests |
| `docker/` | Local supporting services |

The request flow follows normal Django conventions: `config/urls.py` delegates
to app URL modules, a view reads or updates models, and a template renders the
response. Search is exposed at `/search/`; chemical details live under
`/chemicals/`; `/healthz/` is a liveness endpoint and `/readyz/` reports
dependency readiness.

### Authentication and authorization

`accounts.User` is the custom user model. Every user has one primary role:
Student, Faculty, or Admin. Saving a user keeps Django staff status aligned
with that role, and signals synchronize the user with the corresponding
reserved Django group.

Use the model's capability properties, such as `can_manage_inventory`, when
authorization depends on a role. Do not rely on hiding a button in a template;
enforce the same rule in the server-side view.

### Inventory domain

The inventory app currently models chemicals, synonyms, manufacturer products,
SDS links, storage locations, and chemical-to-location assignments. When a
model changes:

```bash
uv run python manage.py makemigrations
uv run python manage.py migrate
uv run pytest
```

Review generated migrations before committing them. Add tests for model
constraints, permissions, query behavior, and the user-visible workflow.

## Typical development workflow

1. Read the relevant model, view, template, and tests before changing code.
2. Make one focused change and add or update tests with it.
3. Create and review a migration when persistent models change.
4. Run the focused test module while iterating, then run the full quality suite.
5. Update the README or this guide when setup, behavior, or architecture changes.
6. Open a pull request that explains the behavior change and any database or
   external-service impact.

Production features must not depend on mock or invented chemical data. Test
fixtures may use representative data, but runtime empty states should remain
honest until real records are available.

Chemical hazards, disposal guidance, and SDS revisions are safety-sensitive
content. Preserve source and revision information and involve the appropriate
institutional owner when changing how that content is stored or presented.

## Frontend changes

Django templates provide the UI, with Bootstrap and project SCSS for styling.
HTMX and Alpine.js are available for progressive interaction where needed.

After changing SCSS, rebuild the application and admin styles:

```bash
make css
```

Commit the relevant source and compiled asset changes together.

## Documentation changes

Documentation is built with MkDocs. Preview it locally with:

```bash
uv run mkdocs serve
```

Before opening a pull request, verify the production build:

```bash
uv run mkdocs build --strict
```

## Troubleshooting

### PostgreSQL connection refused

Confirm that the container is running and that `.env` matches its configured
database, user, password, host, and port:

```bash
docker compose --env-file .env -f docker/docker-compose.yml ps
```

When Django runs on the host, `DB_HOST` should normally be `localhost`. A
container-to-container setup would instead use the Compose service name `db`.

### Port 5432 is already in use

Stop the other PostgreSQL instance or change both the host-side Compose port
and `DB_PORT` to an available port.

### Migrations are out of date

Run the migration check shown above. If you intentionally changed a model,
generate a migration and review it; otherwise, find the uncommitted model or
migration change instead of creating an unrelated migration.

### CSS changes do not appear

Run `make css`, then hard-refresh the browser. Sass must be installed separately
because it is not a Python dependency.

## Before your first pull request

- The application starts against PostgreSQL and the affected workflow works in
  a browser.
- Ruff, ty, pytest, and the migration check pass.
- New behavior has tests, and no production path uses mock data.
- Setup, architecture, and user-facing behavior changes are documented.
- Safety-sensitive changes identify their content source and reviewer.

