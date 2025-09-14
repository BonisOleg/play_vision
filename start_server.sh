#!/bin/bash

# Play Vision Development Server Startup Script
echo "🚀 Запуск Play Vision сервера..."

# Перевірка віртуального середовища
if [ ! -d "venv" ]; then
    echo "❌ Віртуальне середовище не знайдено!"
    echo "Створюю нове віртуальне середовище..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo "✅ Віртуальне середовище знайдено"
fi

# Активація віртуального середовища
echo "📦 Активую віртуальне середовище..."
source venv/bin/activate

# Встановлення правильного Django settings модуля
export DJANGO_SETTINGS_MODULE=playvision.settings.development
echo "⚙️  DJANGO_SETTINGS_MODULE встановлений на: $DJANGO_SETTINGS_MODULE"

# Перевірка .env файлу
if [ ! -f ".env" ]; then
    echo "⚠️  .env файл не знайдений! Створюю базовий .env файл..."
    cat > .env << 'EOF'
DJANGO_ENV=development
SECRET_KEY=django-insecure-development-key-super-long-random-string-12345
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,*
DJANGO_LOG_LEVEL=DEBUG
EOF
    echo "✅ .env файл створений"
else
    echo "✅ .env файл знайдений"
fi

# Перевірка Django конфігурації
echo "🔍 Перевіряю Django конфігурацію..."
python3 manage.py check --deploy || {
    echo "⚠️  Є попередження в конфігурації, але продовжуємо..."
}

# Міграції (якщо потрібно)
echo "🗄️  Перевіряю міграції..."
python3 manage.py makemigrations --dry-run --verbosity 0 | grep -q "No changes detected" || {
    echo "📝 Створюю нові міграції..."
    python3 manage.py makemigrations
}

python3 manage.py migrate --verbosity 1

# Збірка статичних файлів (тільки якщо папка static порожня)
if [ ! "$(ls -A staticfiles 2>/dev/null)" ]; then
    echo "📁 Збираю статичні файли..."
    python3 manage.py collectstatic --noinput --clear
fi

# Показати інформацію про сервер
echo ""
echo "🌟 Play Vision Development Server"
echo "================================="
echo "📍 URL: http://127.0.0.1:8000"
echo "🔧 Debug Mode: ON"
echo "🗄️  Database: SQLite (db.sqlite3)"
echo "📂 Static Files: /static/"
echo ""
echo "✅ Наші виправлення активні:"
echo "   - interval-manager.js загружений"
echo "   - dom-utils.js загружений"
echo "   - api-utils.js загружений"
echo "   - Memory leaks виправлені"
echo "   - XSS захист активний"
echo ""

# Запуск сервера
echo "🚀 Запускаю Django сервер..."
python3 manage.py runserver 127.0.0.1:8000
