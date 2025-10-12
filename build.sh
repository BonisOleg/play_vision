#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit

echo "🔧 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "🗄️ Checking database state..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'playvision.settings.production')
django.setup()
from django.db import connection
from django.core.management import execute_from_command_line
try:
    with connection.cursor() as cursor:
        # Check if events table exists
        cursor.execute(\"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'events');\")
        events_exists = cursor.fetchone()[0]
        print(f'Events table exists: {events_exists}')
        
        # Check migration status
        cursor.execute(\"SELECT * FROM django_migrations WHERE app = 'events' ORDER BY id;\")
        migrations = cursor.fetchall()
        print(f'Events migrations applied: {len(migrations)}')
        for migration in migrations:
            print(f'  - {migration[1]}: {migration[2]}')
            
except Exception as e:
    print(f'⚠️ Database check failed: {e}')
" || echo "Database check failed, continuing..."

echo "🗄️ Running migrations..."
python manage.py migrate

echo "🤖 Loading AI knowledge base..."
python manage.py load_knowledge_base || echo "⚠️ AI knowledge base loading failed, continuing..."

echo "👤 Creating demo data..."
python manage.py setup_initial_data || echo "⚠️ Initial data setup failed, continuing..."
python manage.py create_content_data || echo "⚠️ Content data creation failed, continuing..."

echo "⭐ Creating featured courses..."
python manage.py create_featured_courses || echo "⚠️ Featured courses creation failed, continuing..."

echo "🎉 Build completed successfully!"
