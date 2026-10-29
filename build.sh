#!/usr/bin/env bash
set -o errexit
set -o nounset
set -o pipefail

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py check
python manage.py collectstatic --no-input
python manage.py migrate --noinput
python manage.py create_admin_from_env
