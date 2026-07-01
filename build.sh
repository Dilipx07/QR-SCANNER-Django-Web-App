#!/usr/bin/env bash
set -o errexit

python -m pip install --upgrade pip
pip install -r requirements.txt
python -m manage.py collectstatic --no-input
python -m manage.py migrate --no-input
python -m manage.py seed_scanner_login
