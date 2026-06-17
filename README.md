# QRSCANNER

QRSCANNER is a Django application for managing gas cylinder QR workflows. It supports user login, cylinder stock dashboards, vendor/type masters, inward and outward scanning, stock-in/stock-out actions, and inward/outward history views.

## Features

- Login and logout flow backed by the `Login` app.
- Cylinder stock dashboard at `/QR/Dashboard`.
- Cylinder vendor and gas type lookup endpoints.
- Cylinder inward form, QR validation, submission, and removal.
- Cylinder outward form, QR validation, submission, and stock-out handling.
- Inward/outward history filtering by vendor and date fields.
- PostgreSQL database configuration through environment variables.

## Tech Stack

- Python 3.11
- Django 5.0.6
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
```

Apply database migrations:

```bash
python manage.py migrate
```

Run the development server:

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/Login`.

## Routes

- `/Login` - Login page
- `/Logout` - Logout route
- `/QR/Dashboard` - Cylinder stock dashboard
- `/QR/Cylinder-Inward-Form` - Cylinder inward workflow
- `/QR/Cylinder-Outward-Form` - Cylinder outward workflow
- `/QR/Cylinder-Inward-Outward-History` - Cylinder history view

## Database Notes

This project is configured for PostgreSQL in `QRSCANNER/settings.py`. The required database values are loaded from `.env`.

Do not commit `.env`, `db.sqlite3`, virtual environments, logs, or Python cache files. The repository includes `.gitignore` rules for these local artifacts.

## Deployment Checklist

- Move `SECRET_KEY`, `DEBUG`, and `ALLOWED_HOSTS` to environment variables before production deployment.
- Set `DEBUG=False` in production.
- Configure production static file serving.
- Use a production PostgreSQL database.
- Review session settings and cookie security options.
- Create a real admin route only if the deployment requires Django admin access.

## Tests

Run the Django test suite from the project directory:

```bash
python manage.py test
```

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

