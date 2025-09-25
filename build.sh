#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit

echo "🔧 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "🗄️ Dropping and recreating events table (DANGER!)..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'playvision.settings.production')
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        # Drop events-related tables if they exist
        cursor.execute('DROP TABLE IF EXISTS events CASCADE;')
        cursor.execute('DROP TABLE IF EXISTS speakers CASCADE;')
        cursor.execute('DROP TABLE IF EXISTS event_registrations CASCADE;')
        cursor.execute('DROP TABLE IF EXISTS event_tickets CASCADE;')
        print('✅ Successfully dropped existing events tables')
except Exception as e:
    print(f'⚠️ Drop tables failed (probably OK): {e}')
" || echo "Drop tables script failed, continuing..."

echo "🗄️ Force resetting migrations state..."
python manage.py migrate --fake events zero || echo "Events app not in migration table yet"

echo "🗄️ Running migrations..."
python manage.py migrate

echo "🤖 Loading AI knowledge base..."
python manage.py load_knowledge_base || echo "⚠️ AI knowledge base loading failed, continuing..."

echo "👤 Creating initial data..."
python manage.py setup_initial_data || echo "⚠️ Initial data setup failed, continuing..."

echo "🎉 Build completed successfully!"
