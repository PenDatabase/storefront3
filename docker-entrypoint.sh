#!/bin/bash

# Wait for MySQL to be fully ready
echo "Waiting for MySQL to be ready..."
sleep 10

# Collect static files
echo "Collecting static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Start server with Gunicorn
echo "Starting server with Gunicorn"
gunicorn storefront.wsgi:application --bind 0.0.0.0:8000 --workers 3