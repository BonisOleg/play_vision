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

# Load AI knowledge base
python manage.py load_knowledge_base

# Create superuser if doesn't exist
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@playvision.com').exists():
    User.objects.create_superuser('admin@playvision.com', 'admin@playvision.com', 'changeme123')
    print('Superuser created')
else:
    print('Superuser already exists')

# Create AI configuration if doesn't exist
from apps.ai.models import AIConfiguration
if not AIConfiguration.objects.exists():
    AIConfiguration.objects.create(
        llm_provider='openai',
        llm_model='gpt-3.5-turbo',
        is_enabled=True
    )
    print('AI Configuration created')
else:
    print('AI Configuration already exists')
END
