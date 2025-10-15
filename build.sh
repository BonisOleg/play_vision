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

echo "🗄️ Showing pending migrations..."
python manage.py showmigrations --plan || echo "⚠️ Could not show migrations"

echo "🗄️ Running migrations..."
python manage.py migrate --noinput

echo "✅ Migrations completed. Checking loyalty app tables..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'playvision.settings.production')
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute(\"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'loyalty_accounts');\")
        loyalty_exists = cursor.fetchone()[0]
        print(f'✓ Loyalty accounts table exists: {loyalty_exists}')
        
        cursor.execute(\"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'point_earning_rules');\")
        rules_exists = cursor.fetchone()[0]
        print(f'✓ Point earning rules table exists: {rules_exists}')
        
        if loyalty_exists:
            cursor.execute(\"SELECT column_name FROM information_schema.columns WHERE table_name = 'loyalty_accounts' AND column_name = 'lifetime_spent_points';\")
            col_exists = cursor.fetchone()
            print(f'✓ lifetime_spent_points column exists: {col_exists is not None}')
except Exception as e:
    print(f'⚠️ Loyalty tables check failed: {e}')
" || echo "⚠️ Loyalty check failed, continuing..."

echo "🤖 Loading AI knowledge base..."
python manage.py load_knowledge_base || echo "⚠️ AI knowledge base loading failed, continuing..."

echo "👤 Creating demo data..."
python manage.py setup_initial_data || echo "⚠️ Initial data setup failed, continuing..."
python manage.py create_content_data || echo "⚠️ Content data creation failed, continuing..."

echo "⭐ Creating featured courses..."
python manage.py create_featured_courses || echo "⚠️ Featured courses creation failed, continuing..."

echo "🎉 Build completed successfully!"
