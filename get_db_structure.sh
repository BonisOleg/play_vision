#!/bin/bash
# Скрипт для отримання повної структури production БД з Render

echo "📊 Отримання структури бази даних з Render..."
echo ""

# Отримайте DATABASE_URL з Render Dashboard → Environment
# Замініть нижче на ваш реальний DATABASE_URL
# Формат: postgresql://user:password@host:port/database

# ВАЖЛИВО: Вставте тут ваш DATABASE_URL з Render
DATABASE_URL="YOUR_DATABASE_URL_HERE"

if [ "$DATABASE_URL" = "YOUR_DATABASE_URL_HERE" ]; then
    echo "❌ ПОМИЛКА: Відредагуйте скрипт і вставте ваш DATABASE_URL з Render Dashboard"
    echo ""
    echo "Де знайти DATABASE_URL:"
    echo "1. Відкрийте https://dashboard.render.com"
    echo "2. Виберіть ваш PostgreSQL service"
    echo "3. Скопіюйте 'Internal Database URL' або 'External Database URL'"
    echo "4. Вставте його в цей скрипт замість YOUR_DATABASE_URL_HERE"
    exit 1
fi

echo "1️⃣ Список всіх таблиць:"
echo "========================"
psql "$DATABASE_URL" -c "
SELECT schemaname, tablename 
FROM pg_tables 
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY tablename;
"

echo ""
echo "2️⃣ Структура таблиці users:"
echo "============================"
psql "$DATABASE_URL" -c "\d users"

echo ""
echo "3️⃣ Структура таблиці subscription_plans:"
echo "=========================================="
psql "$DATABASE_URL" -c "\d subscription_plans"

echo ""
echo "4️⃣ Перевірка таблиці user_subscriptions:"
echo "========================================="
psql "$DATABASE_URL" -c "
SELECT EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_name='user_subscriptions'
);
"

echo ""
echo "5️⃣ Структура таблиці event_registrations:"
echo "==========================================="
psql "$DATABASE_URL" -c "\d event_registrations"

echo ""
echo "6️⃣ Всі колонки в subscription_plans:"
echo "====================================="
psql "$DATABASE_URL" -c "
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'subscription_plans'
ORDER BY ordinal_position;
"

echo ""
echo "7️⃣ Всі колонки в event_registrations:"
echo "======================================"
psql "$DATABASE_URL" -c "
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns
WHERE table_name = 'event_registrations'
ORDER BY ordinal_position;
"

echo ""
echo "8️⃣ Застосовані міграції Django:"
echo "================================"
psql "$DATABASE_URL" -c "
SELECT app, name, applied 
FROM django_migrations 
WHERE app IN ('events', 'subscriptions')
ORDER BY id DESC 
LIMIT 20;
"

echo ""
echo "✅ Готово! Скопіюйте весь вивід і надішліть мені."

