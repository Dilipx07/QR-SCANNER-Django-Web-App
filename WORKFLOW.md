# Workflow

This document describes the development and release workflow for the Gas Cylinder Scanner Django project.

## Development Flow

1. Create or update code in a focused branch.
2. Keep local secrets in `.env`; use `.env.example` for shared configuration names.
3. Add Django migrations for model or seed-data changes.
4. For inward/outward workflow changes, verify the backend stock transitions and the dashboard/report analytics together.
5. Run tests before committing.
6. Commit with a short developer-readable summary and a concise body when useful.
7. Push to `origin/main` or open a pull request.

## Inward / Outward Flow

1. Inward scans create pending cylinder records tied to inward details.
2. Stock-in confirms selected pending inward cylinders and records the stock-in time.
3. Outward scans only allow cylinders that are inwarded, stocked in, and not already outwarded.
4. Stock-out requires selected pending outward cylinders plus a return DC number and records the stock-out time.
5. Dashboard and report analytics use the same cylinder movement states so counts, timing, and stock health remain aligned.

## Seed Data Flow

`Cylinder_Type_Master` seed data is managed through Django migrations. Running migrations inserts the standard gas cylinder types:

1. Oxygen
2. Nitrogen
3. Carbon Dioxide
4. Argon
5. Hydrogen
6. Helium
7. LPG
8. Acetylene

Apply seed data with:

```bash
python manage.py migrate
```

## Test Flow

Run the test suite from the repository root:

```bash
python manage.py test
```

For this project, tests should verify both workflow behavior and required master data such as cylinder type seeds.

Inward/outward changes should include tests for analytics summaries, chart datasets, and stock transition validation.

## Security Flow

Run these checks before pushing authentication, dependency, or deployment changes:

```bash
python manage.py check --deploy
python -m pip_audit -r requirements.txt
python -m bandit -r Login QR QRSCANNER -x QRSCANNER/static,QR/migrations,Login/migrations -ll
```

Fix any reported high, medium, or dependency vulnerability before release.

## Release Flow

Before pushing:

```bash
git status
python manage.py test
git add .
git commit
git push
```

Confirm that `.env`, local databases, virtual environments, and generated Python cache files are not staged.
