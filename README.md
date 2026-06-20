# QRSCANNER

QRSCANNER is the Gas Cylinder Scanner, a Django application for managing gas cylinder QR workflows. It supports user login, cylinder stock dashboards, vendor/type masters, inward and outward scanning, stock-in/stock-out actions, and inward/outward history views.

## Features

- Login and logout flow backed by the `Login` app with Django password hashing.
- Protected QR routes with automatic logout after session expiry.
- Cylinder stock dashboard at `/QR/Dashboard` with stock health, inward/outward timing, vendor mix, and gas-type charts.
- Cylinder vendor and gas type lookup endpoints.
- Cylinder inward form, QR validation, submission, stock-in status cards, and removal.
- Cylinder outward form, QR validation, submission, stock-out status cards, and return DC handling.
- Inward/outward intelligence report with filters, KPI cards, charts, insights, and a detailed movement ledger.
- Seeded gas cylinder type master data through Django migrations.
- PostgreSQL database configuration through environment variables.
- Optional SQLite database mode through `DB_ENGINE=sqlite`.
- Render-ready deployment blueprint with `/health/` monitoring and a 5-second internal health-check scheduler.

## Tech Stack

- Python 3.11
- Django 5.2.15
- PostgreSQL
- Pipenv or `pip` with `requirements.txt`
- Bootstrap and vendored static assets

## Project Structure

```text
QRSCANNER/
├── Login/              # Login models, routes, and views
├── QR/                 # Cylinder QR workflow models, routes, and views
├── QRSCANNER/          # Django project settings and root URL configuration
├── static/             # Collected/static assets used by templates
├── templates/          # Django templates
├── manage.py
└── requirements.txt
```

## Prerequisites

- Python 3.11
- PostgreSQL server
- Git
- Optional: Pipenv

## Local Setup

Clone the repository and move into the Django project directory:

```bash
git clone <repository-url>
cd QRSCANNER
```

Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create an environment file:

```bash
copy .env.example .env
```

Update `.env` with your PostgreSQL database credentials:

```env
DB_NAME=qrscanner
DB_USER=postgres
DB_USER_PASSWORD=change-me
DB_HOST=127.0.0.1
DB_PORT=5432
DB_ENGINE=postgresql
SQLITE_NAME=db.sqlite3
SECRET_KEY=change-me-to-a-long-random-secret
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
SESSION_COOKIE_AGE=86400
HEALTH_CHECK_INTERVAL_SECONDS=5
HEALTH_CHECK_SCHEDULER_ENABLED=True
HEALTH_CHECK_URL=http://127.0.0.1:8000/health/
```

`DEBUG` defaults to `False` when it is not set. Keep `DEBUG=True` only in local development.

Apply database migrations:

```bash
python manage.py migrate
```

Migrations also seed the standard `Cylinder_Type_Master` records used by the Gas Cylinder Scanner workflow.

Run the development server:

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/Login`.

## Authentication

The application uses the existing `Login.qr_scanner_login` table for scanner users, but passwords are stored with Django's password hashers instead of plaintext. Existing plaintext passwords are converted to hashes by the `Login.0003_hash_existing_login_passwords` migration.

QR workflow routes under `/QR/` require a valid login session. Sessions are refreshed on activity and automatically redirected to `/Login` after `SESSION_COOKIE_AGE` seconds of inactivity.

## Routes

- `/Login` - Login page
- `/Logout` - Logout route
- `/QR/Dashboard` - Cylinder stock dashboard
- `/QR/Cylinder-Inward-Form` - Cylinder inward workflow
- `/QR/Cylinder-Outward-Form` - Cylinder outward workflow
- `/QR/Cylinder-Inward-Outward-History` - Cylinder inward/outward intelligence report
- `/health/` - JSON health-check endpoint for Render and uptime monitoring

## Render Deployment

The repository includes the files Render needs:

- `render.yaml` - Blueprint for the Django web service and PostgreSQL database.
- `build.sh` - Installs dependencies and runs `collectstatic`.
- `requirements.txt` - Includes `gunicorn` for production WSGI and `whitenoise` for static files.

Deploy from the Render dashboard using the repository Blueprint. Render will provision `qrscanner-db`, inject database credentials, run migrations on service start, and monitor `/health/`.

The app also starts a lightweight scheduler in server processes. By default it hits `/health/` every 5 seconds using `HEALTH_CHECK_URL`, `RENDER_EXTERNAL_HOSTNAME`, or the local `$PORT` fallback. Set `HEALTH_CHECK_SCHEDULER_ENABLED=False` to disable it.

## Database Notes

This project keeps PostgreSQL support in `QRSCANNER/settings.py`. Use `DB_ENGINE=postgresql` with `DB_NAME`, `DB_USER`, `DB_USER_PASSWORD`, `DB_HOST`, and `DB_PORT` for PostgreSQL.

Use `DB_ENGINE=sqlite` to run with SQLite. On Render, the included `render.yaml` uses SQLite at `/opt/render/project/src/db.sqlite3`.

Render filesystem storage is not a durable database strategy. SQLite is acceptable for a quick proof of deployment, but production data should move back to PostgreSQL or a persistent disk.

Do not commit `.env`, `db.sqlite3`, virtual environments, logs, or Python cache files. The repository includes `.gitignore` rules for these local artifacts.

## Deployment Checklist

- Move `SECRET_KEY`, `DEBUG`, and `ALLOWED_HOSTS` to environment variables before production deployment.
- Set `DEBUG=False` in production.
- Set `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`, and `SECURE_SSL_REDIRECT=True` when serving over HTTPS.
- Configure production static file serving.
- Keep `/health/` publicly reachable for Render health checks.
- Use a production PostgreSQL database for durable production data.
- Review session settings and cookie security options.
- Create a real admin route only if the deployment requires Django admin access.

## Tests

Run the Django test suite from the project directory:

```bash
python manage.py test
```

Run security checks:

```bash
python manage.py check --deploy
python -m pip_audit -r requirements.txt
python -m bandit -r Login QR QRSCANNER -x QRSCANNER/static,QR/migrations,Login/migrations -ll
```

## Workflow

See `WORKFLOW.md` for the development, seed-data, test, and release workflow.

## GitHub Push Checklist

Before pushing:

```bash
git status
git add README.md .gitignore .env.example CONTRIBUTING.md SECURITY.md CHANGELOG.md CODE_OF_CONDUCT.md .github/
git add Login QR QRSCANNER templates static manage.py requirements.txt
git commit -m "Prepare project for GitHub"
git remote add origin <repository-url>
git branch -M main
git push -u origin main
```

Review `git status` carefully before committing so local secrets and database files are not staged.
