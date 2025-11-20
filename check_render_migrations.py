#!/usr/bin/env python
"""
Скрипт діагностики міграцій для Render
Використання: python check_render_migrations.py
"""
import os
import django
import sys
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'playvision.settings.production')
django.setup()

from django.core.management import call_command
from django.db import connection, migrations
from django.apps import apps
from django.db.migrations.recorder import MigrationRecorder

def check_database_connection():
    """Перевірка підключення до БД"""
    print("=" * 80)
    print("📊 ПЕРЕВІРКА ПІДКЛЮЧЕННЯ ДО БД")
    print("=" * 80)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ PostgreSQL версія: {version[0]}")
            
            cursor.execute("SELECT current_database();")
            db_name = cursor.fetchone()
            print(f"✅ База даних: {db_name[0]}")
            
            return True
    except Exception as e:
        print(f"❌ Помилка підключення: {e}")
        return False

def check_migration_table():
    """Перевірка таблиці django_migrations"""
    print("\n" + "=" * 80)
    print("📋 ТАБЛИЦЯ DJANGO_MIGRATIONS")
    print("=" * 80)
    try:
        recorder = MigrationRecorder(connection)
        applied = recorder.applied_migrations()
        print(f"✅ Застосовано міграцій: {len(applied)}")
        
        # Групуємо по app
        apps_migrations = {}
        for app, name in applied:
            if app not in apps_migrations:
                apps_migrations[app] = []
            apps_migrations[app].append(name)
        
        print("\n📦 По додатках:")
        for app_name in sorted(apps_migrations.keys()):
            migrations_list = sorted(apps_migrations[app_name])
            print(f"  {app_name}: {len(migrations_list)} міграцій")
            
        return apps_migrations
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return {}

def check_app_migrations(app_label):
    """Перевірка міграцій конкретного додатку"""
    print(f"\n{'─' * 80}")
    print(f"📱 APP: {app_label}")
    print(f"{'─' * 80}")
    
    try:
        # Файлові міграції
        app_config = apps.get_app_config(app_label)
        migrations_path = Path(app_config.path) / 'migrations'
        
        if migrations_path.exists():
            migration_files = sorted([
                f.stem for f in migrations_path.glob('*.py')
                if f.stem != '__init__' and not f.stem.startswith('.')
            ])
            print(f"📁 Файлів міграцій: {len(migration_files)}")
            for mig in migration_files:
                print(f"   • {mig}")
        else:
            print(f"⚠️  Директорія міграцій не існує")
            migration_files = []
        
        # Застосовані міграції
        recorder = MigrationRecorder(connection)
        applied = [
            name for app, name in recorder.applied_migrations()
            if app == app_label
        ]
        applied_sorted = sorted(applied)
        print(f"\n✅ Застосовано в БД: {len(applied_sorted)}")
        for mig in applied_sorted:
            print(f"   ✓ {mig}")
        
        # Незастосовані
        file_set = set(migration_files)
        applied_set = set(applied)
        
        unapplied = file_set - applied_set
        if unapplied:
            print(f"\n⚠️  НЕЗАСТОСОВАНІ міграції ({len(unapplied)}):")
            for mig in sorted(unapplied):
                print(f"   ⚠️  {mig}")
        
        # Застосовані, але відсутні файли
        missing = applied_set - file_set
        if missing:
            print(f"\n❌ ВІДСУТНІ ФАЙЛИ (застосовано в БД, але немає у коді) ({len(missing)}):")
            for mig in sorted(missing):
                print(f"   ❌ {mig}")
        
        return {
            'files': migration_files,
            'applied': applied_sorted,
            'unapplied': list(unapplied),
            'missing': list(missing)
        }
        
    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
        return None

def check_tables():
    """Перевірка наявності таблиць"""
    print("\n" + "=" * 80)
    print("🗄️  ТАБЛИЦІ В БД")
    print("=" * 80)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            print(f"✅ Всього таблиць: {len(tables)}")
            
            # Групуємо по app
            app_tables = {}
            for table in tables:
                if '_' in table:
                    app_name = table.split('_')[0]
                    if app_name not in app_tables:
                        app_tables[app_name] = []
                    app_tables[app_name].append(table)
            
            print("\n📊 По додатках:")
            for app_name in sorted(app_tables.keys()):
                print(f"\n  {app_name.upper()} ({len(app_tables[app_name])} таблиць):")
                for table in sorted(app_tables[app_name]):
                    print(f"    • {table}")
            
            return tables
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return []

def main():
    print("\n" + "=" * 80)
    print("🔍 ДІАГНОСТИКА МІГРАЦІЙ PLAY VISION на RENDER")
    print("=" * 80)
    print()
    
    # 1. Перевірка БД
    if not check_database_connection():
        sys.exit(1)
    
    # 2. Таблиця міграцій
    apps_migrations = check_migration_table()
    
    # 3. Таблиці
    tables = check_tables()
    
    # 4. Детальна перевірка критичних app
    critical_apps = ['accounts', 'subscriptions', 'events', 'content', 'cms', 'mentoring']
    
    print("\n" + "=" * 80)
    print("🔬 ДЕТАЛЬНА ПЕРЕВІРКА ДОДАТКІВ")
    print("=" * 80)
    
    results = {}
    for app_label in critical_apps:
        try:
            results[app_label] = check_app_migrations(app_label)
        except Exception as e:
            print(f"❌ Помилка для {app_label}: {e}")
    
    # 5. Підсумок
    print("\n" + "=" * 80)
    print("📝 ПІДСУМОК")
    print("=" * 80)
    
    issues = []
    for app_label, result in results.items():
        if result:
            if result['unapplied']:
                issues.append(f"❌ {app_label}: {len(result['unapplied'])} незастосованих міграцій")
            if result['missing']:
                issues.append(f"⚠️  {app_label}: {len(result['missing'])} відсутніх файлів міграцій")
    
    if issues:
        print("\n⚠️  ВИЯВЛЕНІ ПРОБЛЕМИ:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n✅ Міграції в порядку!")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    main()

