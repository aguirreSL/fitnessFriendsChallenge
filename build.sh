#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -o errexit

# Ensure the script itself has executable permissions
chmod +x build.sh

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

python manage.py makemigrations

# Run database migrations
python manage.py migrate

# Create superuser if it doesn't exist
if [[ CREATE_SUPERUSER ]];
then 
    python manage.py createsuperuser --no-input --email "$DJANGO_SUPERUSER_EMAIL"
fi
