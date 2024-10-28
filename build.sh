#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -o errexit

# Ensure the script itself has executable permissions
chmod +x build.sh

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run database migrations
# python manage.py makemigrations
python manage.py migrate

# Create superuser if it doesn't exist
if [ "$CREATE_SUPERUSER" = "TRUE" ]; then
    python manage.py createsuperuser --no-input --email "$DJANGO_SUPERUSER_EMAIL" --username "$DJANGO_SUPERUSER_USERNAME"
fi
