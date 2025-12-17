#!/usr/bin/env bash
# Перевірка стану міграцій на Render
# Використання: render shell playvision -- './render_check_migrations.sh'

set -o errexit

echo "=========================================="
echo "🔍 ПЕРЕВІРКА МІГРАЦІЙ НА RENDER"
echo "=========================================="
echo ""

# 1. Список всіх міграцій subscriptions
echo "1️⃣ Всі міграції subscriptions (локальні файли)..."
ls -1 apps/subscriptions/migrations/0*.py | sort -V
echo ""

# 2. Застосовані міграції в БД
echo "2️⃣ Застосовані міграції в БД..."
python manage.py showmigrations subscriptions
echo ""

# 3. План міграцій
echo "3️⃣ План міграцій (які будуть застосовані)..."
python manage.py showmigrations --plan | grep subscriptions || echo "Немає незастосованих міграцій"
echo ""

# 4. Остання застосована міграція
echo "4️⃣ Остання застосована міграція subscriptions..."
python manage.py dbshell <<EOF
SELECT name, applied 
FROM django_migrations 
WHERE app = 'subscriptions' 
ORDER BY applied DESC 
LIMIT 1;
\q
EOF
echo ""

# 5. Всі застосовані міграції з датами
echo "5️⃣ Всі застосовані міграції з датами..."
python manage.py dbshell <<EOF
SELECT 
    name, 
    applied,
    CASE 
        WHEN name LIKE '0001%' THEN 'Initial'
        WHEN name LIKE '0002%' THEN 'Add missing fields'
        WHEN name LIKE '0003%' THEN 'Remove duration'
        WHEN name LIKE '0004%' THEN 'Remove duration_months'
        WHEN name LIKE '0005%' THEN 'Verify table'
        WHEN name LIKE '0006%' THEN 'Cleanup columns'
        WHEN name LIKE '0007%' THEN 'Make nullable'
        WHEN name LIKE '0018%' THEN 'Add features 6-30'
        WHEN name LIKE '0019%' THEN 'Add period features'
        WHEN name LIKE '0020%' THEN 'Remove old features'
        ELSE 'Other'
    END as description
FROM django_migrations 
WHERE app = 'subscriptions' 
ORDER BY name;
\q
EOF
echo ""

# 6. Перевірка конфліктів (пропущені міграції)
echo "6️⃣ Перевірка на пропущені міграції..."
python manage.py dbshell <<EOF
-- Знайти міграції які є в файлах але не застосовані
WITH file_migrations AS (
    SELECT unnest(ARRAY[
        '0001_initial',
        '0002_add_missing_fields',
        '0003_remove_duration_field',
        '0004_remove_duration_months',
        '0005_verify_subscriptions_table',
        '0006_cleanup_old_columns',
        '0007_make_old_fields_nullable',
        '0018_add_features_6_to_30'
    ]) as migration_name
),
applied_migrations AS (
    SELECT name FROM django_migrations WHERE app = 'subscriptions'
)
SELECT 
    fm.migration_name,
    CASE 
        WHEN am.name IS NULL THEN '❌ НЕ ЗАСТОСОВАНА'
        ELSE '✅ Застосована'
    END as status
FROM file_migrations fm
LEFT JOIN applied_migrations am ON fm.migration_name = am.name
ORDER BY fm.migration_name;
\q
EOF
echo ""

echo "=========================================="
echo "✅ ПЕРЕВІРКА ЗАВЕРШЕНА"
echo "=========================================="

