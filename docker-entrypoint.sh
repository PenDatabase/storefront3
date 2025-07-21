#!/bin/bash

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Start server with Gunicorn
echo "Starting server with Gunicorn"
gunicorn storefront.wsgi:application --bind 0.0.0.0:8000 --workers 3