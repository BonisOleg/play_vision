#!/bin/bash
# Post-deploy migration script for Render
# This script will be run after deployment to fix database schema issues

set -e

echo "🔄 Running database migrations..."

# Run migrations
python manage.py migrate subscriptions --noinput

echo "✅ Migrations completed successfully!"

# Check if tables exist
python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()

# Check subscription_plans table
cursor.execute(\"SELECT column_name FROM information_schema.columns WHERE table_name='subscription_plans' ORDER BY column_name\")
print('📋 Columns in subscription_plans table:')
for row in cursor.fetchall():
    print(f'  - {row[0]}')

# Check user_subscriptions table
cursor.execute(\"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='user_subscriptions')\")
exists = cursor.fetchone()[0]
print(f'\\n📋 user_subscriptions table exists: {exists}')
"

echo "✅ Database schema check completed!"

