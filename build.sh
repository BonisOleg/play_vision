#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create superuser if doesn't exist
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@playvision.com').exists():
    User.objects.create_superuser('admin@playvision.com', 'admin@playvision.com', 'changeme123')
    print('Superuser created')
else:
    print('Superuser already exists')
END
