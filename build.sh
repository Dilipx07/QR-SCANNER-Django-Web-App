#!/usr/bin/env bash
set -o errexit

python -m pip install --upgrade pip
python -m pip install -r requirements-render.txt

python manage.py collectstatic --no-input
python manage.py migrate --no-input
python manage.py seed_scanner_login
