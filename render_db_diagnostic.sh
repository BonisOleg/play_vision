#!/usr/bin/env bash
# Діагностика бази даних на Render для підготовки міграцій
# Використання: render shell playvision -- './render_db_diagnostic.sh'

set -o errexit

echo "=========================================="
echo "🔍 ДІАГНОСТИКА БД PLAY VISION НА RENDER"
echo "=========================================="
echo ""

# 1. Перевірка з'єднання
echo "1️⃣ Перевірка з'єднання з БД..."
python manage.py dbshell <<EOF
SELECT version();
\q
EOF
echo "✅ З'єднання успішне"
echo ""

# 2. Перевірка таблиці subscription_plans
echo "2️⃣ Структура таблиці subscription_plans..."
python manage.py dbshell <<EOF
SELECT 
    column_name, 
    data_type, 
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_name = 'subscription_plans' 
ORDER BY ordinal_position;
\q
EOF
echo ""

# 3. Перевірка існуючих feature полів
echo "3️⃣ Існуючі feature поля (feature_1 до feature_30)..."
python manage.py dbshell <<EOF
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'subscription_plans' 
  AND column_name LIKE 'feature_%'
ORDER BY 
  CASE 
    WHEN column_name ~ '^feature_[0-9]+$' THEN 
      CAST(SUBSTRING(column_name FROM 'feature_([0-9]+)') AS INTEGER)
    ELSE 999
  END,
  column_name;
\q
EOF
echo ""

# 4. Перевірка полів для знижок
echo "4️⃣ Існуючі поля для знижок..."
python manage.py dbshell <<EOF
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name = 'subscription_plans' 
  AND (column_name LIKE '%discount%' OR column_name LIKE '%price%')
ORDER BY column_name;
\q
EOF
echo ""

# 5. Перевірка міграцій subscriptions
echo "5️⃣ Застосовані міграції для subscriptions..."
python manage.py dbshell <<EOF
SELECT app, name, applied 
FROM django_migrations 
WHERE app = 'subscriptions' 
ORDER BY name;
\q
EOF
echo ""

# 6. Перевірка даних в subscription_plans
echo "6️⃣ Кількість записів та приклад даних..."
python manage.py dbshell <<EOF
SELECT COUNT(*) as total_plans FROM subscription_plans;
SELECT id, name, slug, base_price_uah, discount_3_months, discount_12_months 
FROM subscription_plans 
LIMIT 5;
\q
EOF
echo ""

# 7. Перевірка чи є дані в feature полях
echo "7️⃣ Перевірка заповненості feature полів..."
python manage.py dbshell <<EOF
SELECT 
    id,
    name,
    CASE WHEN feature_1 IS NOT NULL AND feature_1 != '' THEN '✓' ELSE '✗' END as f1,
    CASE WHEN feature_2 IS NOT NULL AND feature_2 != '' THEN '✓' ELSE '✗' END as f2,
    CASE WHEN feature_3 IS NOT NULL AND feature_3 != '' THEN '✓' ELSE '✗' END as f3,
    CASE WHEN feature_4 IS NOT NULL AND feature_4 != '' THEN '✓' ELSE '✗' END as f4,
    CASE WHEN feature_5 IS NOT NULL AND feature_5 != '' THEN '✓' ELSE '✗' END as f5,
    CASE WHEN feature_6 IS NOT NULL AND feature_6 != '' THEN '✓' ELSE '✗' END as f6,
    CASE WHEN feature_30 IS NOT NULL AND feature_30 != '' THEN '✓' ELSE '✗' END as f30
FROM subscription_plans
LIMIT 10;
\q
EOF
echo ""

# 8. Перевірка індексів
echo "8️⃣ Індекси на subscription_plans..."
python manage.py dbshell <<EOF
SELECT 
    indexname, 
    indexdef 
FROM pg_indexes 
WHERE tablename = 'subscription_plans';
\q
EOF
echo ""

# 9. Перевірка обмежень (constraints)
echo "9️⃣ Обмеження на subscription_plans..."
python manage.py dbshell <<EOF
SELECT 
    conname as constraint_name,
    contype as constraint_type,
    pg_get_constraintdef(oid) as constraint_definition
FROM pg_constraint 
WHERE conrelid = 'subscription_plans'::regclass;
\q
EOF
echo ""

# 10. Підсумок для міграцій
echo "🔟 Підсумок для підготовки міграцій..."
python manage.py dbshell <<EOF
-- Перевірка чи існують нові поля які ми плануємо додати
SELECT 
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'subscription_plans' 
        AND column_name = 'feature_1_monthly'
    ) THEN '⚠️ feature_1_monthly вже існує' 
    ELSE '✅ feature_1_monthly не існує (можна додавати)' 
    END as check_feature_1_monthly;

SELECT 
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'subscription_plans' 
        AND column_name = 'discount_monthly_percentage'
    ) THEN '⚠️ discount_monthly_percentage вже існує' 
    ELSE '✅ discount_monthly_percentage не існує (можна додавати)' 
    END as check_discount_monthly;
\q
EOF
echo ""

echo "=========================================="
echo "✅ ДІАГНОСТИКА ЗАВЕРШЕНА"
echo "=========================================="
echo ""
echo "📋 Наступні кроки:"
echo "1. Перевірити вивід вище"
echo "2. Переконатися що feature_1-30 існують"
echo "3. Переконатися що нові поля (feature_X_monthly, feature_X_3months) НЕ існують"
echo "4. Створити міграцію 0019 для додавання нових полів"
echo "5. Створити міграцію 0020 для видалення старих полів (після міграції даних)"

