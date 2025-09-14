#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Set development environment variables
export DJANGO_ENV=development
export DEBUG=True
export DJANGO_SETTINGS_MODULE=playvision.settings.development

# Print current settings for debugging
echo "🚀 Starting Play Vision Development Server"
echo "📁 Working directory: $(pwd)"
echo "🔧 DJANGO_ENV: $DJANGO_ENV"
echo "🐛 DEBUG: $DEBUG"
echo "⚙️  DJANGO_SETTINGS_MODULE: $DJANGO_SETTINGS_MODULE"
echo ""

# Run Django development server
python manage.py runserver 127.0.0.1:8000
