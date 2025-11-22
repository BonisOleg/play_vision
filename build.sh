#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit

echo "🔧 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🌍 Downloading GeoIP database..."
mkdir -p geoip
wget -q https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-Country.mmdb -O geoip/GeoLite2-Country.mmdb || echo "⚠️ GeoIP download failed, using fallback"
chmod 644 geoip/GeoLite2-Country.mmdb || true

echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "👤 Creating superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@playvision.com', 'QwErTy1357')
    print('✅ Superuser created: admin')
else:
    print('⚠️ Superuser already exists')
" || echo "⚠️ Superuser creation skipped"

echo "🗄️ Database connection check..."
python -c "
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'playvision.settings.production')
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
        print('✓ Database connection successful')
except Exception as e:
    print(f'⚠️ Database connection failed: {e}')
    exit(1)
" || exit 1

echo "🗄️ Showing pending migrations..."
python manage.py showmigrations --plan || echo "⚠️ Could not show migrations"

echo "✓ Skipping manual migration fixes - using Django's built-in migration system"

echo "🗄️ Running migrations..."
# Use fake-initial to skip migrations if tables already exist
python manage.py migrate --fake-initial --noinput

echo "💾 Creating cache table for DatabaseCache fallback..."
python manage.py createcachetable || echo "⚠️ Cache table already exists or creation failed, continuing..."

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

echo "📅 Updating production events..."
python manage.py update_production_events || echo "⚠️ Events update failed, continuing..."

echo "🎫 Creating test events..."
python manage.py create_test_events || echo "⚠️ Test events creation failed, continuing..."

echo "🎉 Build completed successfully!"
