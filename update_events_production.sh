#!/bin/bash
# Скрипт для оновлення подій на production через Render shell

echo "📅 Оновлення подій на production..."
echo ""
echo "Команди для запуску в Render Shell:"
echo "======================================"
echo ""
echo "# 1. Оновити існуючі події:"
echo "python manage.py update_production_events"
echo ""
echo "# 2. Створити нові тестові події:"
echo "python manage.py create_test_events"
echo ""
echo "# 3. Перевірити результат:"
echo "python manage.py shell -c \"from apps.events.models import Event; print(f'Всього подій: {Event.objects.count()}'); print(f'З категоріями: {Event.objects.exclude(event_category=\"\").count()}')\""
echo ""
echo "======================================"
echo ""
echo "АБО запустіть через render CLI:"
echo "render shell -c 'python manage.py update_production_events && python manage.py create_test_events'"


