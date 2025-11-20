#!/bin/bash
#
# Скрипт діагностики міграцій та БД на Render
# Використання: ./diagnose_render_db.sh
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=================================================="
echo "🔍 ДІАГНОСТИКА RENDER - Play Vision"
echo "=================================================="
echo ""

# Крок 1: Знайти сервіс
echo -e "${BLUE}Крок 1: Пошук сервісу Play Vision...${NC}"
echo ""
SERVICE_NAME="playvision"

# Спробувати отримати статус
echo -e "${YELLOW}Виконую: render services list${NC}"
render services list

echo ""
echo -e "${YELLOW}Перевірка статусу сервісу '$SERVICE_NAME'...${NC}"
render service status $SERVICE_NAME || echo -e "${RED}❌ Сервіс не знайдено або suspended${NC}"

echo ""
read -p "Продовжити діагностику? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 0
fi

# Крок 2: Логи останнього deploy
echo ""
echo "=================================================="
echo -e "${BLUE}Крок 2: Логи останнього deploy${NC}"
echo "=================================================="
echo ""
echo -e "${YELLOW}Виконую: render logs $SERVICE_NAME --tail 200${NC}"
render logs $SERVICE_NAME --tail 200 | grep -i -E "(migration|error|failed|success)" || echo "Логів немає"

echo ""
read -p "Продовжити? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 0
fi

# Крок 3: Підключення до Django shell
echo ""
echo "=================================================="
echo -e "${BLUE}Крок 3: Django Shell - Перевірка міграцій${NC}"
echo "=================================================="
echo ""
echo -e "${GREEN}Запускаю скрипт діагностики...${NC}"
echo ""

# Завантажити скрипт на сервер і виконати
echo -e "${YELLOW}render shell $SERVICE_NAME -- 'python manage.py showmigrations --list'${NC}"
render shell $SERVICE_NAME -- 'python manage.py showmigrations --list' || echo -e "${RED}❌ Не вдалося виконати${NC}"

echo ""
read -p "Продовжити детальну перевірку? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 0
fi

# Крок 4: Запуск Python скрипта діагностики
echo ""
echo "=================================================="
echo -e "${BLUE}Крок 4: Детальна діагностика (Python)${NC}"
echo "=================================================="
echo ""
echo -e "${YELLOW}Завантажую check_render_migrations.py на Render...${NC}"

# Створити тимчасовий скрипт
cat > /tmp/render_check.py << 'EOFPYTHON'
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'playvision.settings.production')
django.setup()

from django.core.management import call_command
from django.db.migrations.recorder import MigrationRecorder
from django.db import connection

print("=" * 80)
print("SHOWMIGRATIONS")
print("=" * 80)
call_command('showmigrations', '--list')

print("\n" + "=" * 80)
print("МІГРАЦІЇ В БД")
print("=" * 80)
recorder = MigrationRecorder(connection)
applied = recorder.applied_migrations()
apps_mig = {}
for app, name in applied:
    if app not in apps_mig:
        apps_mig[app] = []
    apps_mig[app].append(name)

for app in sorted(apps_mig.keys()):
    print(f"\n{app}:")
    for mig in sorted(apps_mig[app]):
        print(f"  ✓ {mig}")
EOFPYTHON

echo -e "${YELLOW}render shell $SERVICE_NAME < /tmp/render_check.py${NC}"
render shell $SERVICE_NAME < /tmp/render_check.py || echo -e "${RED}❌ Помилка виконання${NC}"

rm -f /tmp/render_check.py

# Крок 5: Перевірка БД через psql
echo ""
echo "=================================================="
echo -e "${BLUE}Крок 5: Прямий доступ до PostgreSQL${NC}"
echo "=================================================="
echo ""
echo -e "${YELLOW}Для прямого доступу до БД виконайте:${NC}"
echo ""
echo "1. Отримайте DATABASE_URL з Render Dashboard:"
echo "   https://dashboard.render.com → playvision → Environment → DATABASE_URL"
echo ""
echo "2. Підключіться через psql:"
echo "   psql \$DATABASE_URL"
echo ""
echo "3. Виконайте SQL запити:"
echo "   SELECT app, name FROM django_migrations ORDER BY app, name;"
echo "   \\dt"
echo "   \\d cms_eventgridcell"
echo ""

# Крок 6: Рекомендації
echo ""
echo "=================================================="
echo -e "${GREEN}📋 РЕКОМЕНДАЦІЇ${NC}"
echo "=================================================="
echo ""
echo "Якщо виявлені проблеми з міграціями:"
echo ""
echo "1. Незастосовані міграції → запустити:"
echo "   render shell $SERVICE_NAME -- 'python manage.py migrate'"
echo ""
echo "2. Розрив у ланцюгу міграцій CMS (0002-0005, 0007-0009) → створити dummy:"
echo "   python manage.py makemigrations cms --empty --name dummy_02"
echo ""
echo "3. Конфлікти → squash міграції:"
echo "   python manage.py squashmigrations cms 0001 0010"
echo ""
echo "4. Критичні помилки → rollback до попередньої версії коду"
echo ""

echo -e "${GREEN}✅ Діагностика завершена${NC}"

