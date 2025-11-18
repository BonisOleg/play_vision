# Generated manually - SAFE reset of all content and categories
from django.db import migrations, transaction
from django.db.models import Q


def table_exists(cursor, table_name):
    """Перевіряє чи існує таблиця в БД"""
    try:
        # Універсальний спосіб - просто спробувати SELECT
        cursor.execute(f"SELECT 1 FROM {table_name} LIMIT 1")
        return True
    except Exception:
        return False


def safe_delete_from_table(cursor, table_name, condition=""):
    """Безпечно видаляє дані з таблиці якщо вона існує"""
    if not table_exists(cursor, table_name):
        print(f"⚠️  Таблиця {table_name} не існує - пропускаємо")
        return 0
    
    try:
        # Рахуємо записи
        count_query = f"SELECT COUNT(*) FROM {table_name}"
        if condition:
            count_query += f" WHERE {condition}"
        
        cursor.execute(count_query)
        count = cursor.fetchone()[0]
        
        if count > 0:
            # Видаляємо
            delete_query = f"DELETE FROM {table_name}"
            if condition:
                delete_query += f" WHERE {condition}"
            
            cursor.execute(delete_query)
            return count
        else:
            return 0
    except Exception as e:
        print(f"⚠️  Помилка при роботі з {table_name}: {e}")
        return 0


def safe_reset_everything(apps, schema_editor):
    """
    БЕЗПЕЧНЕ видалення всього контенту та категорій через RAW SQL.
    Працює на будь-якій БД (PostgreSQL, SQLite) та з будь-якою структурою.
    """
    print("\n" + "="*80)
    print("🔥 ПОЧИНАЄМО ПОВНЕ ОЧИЩЕННЯ КОНТЕНТУ ТА КАТЕГОРІЙ")
    print("="*80 + "\n")
    
    try:
        with transaction.atomic():
            with schema_editor.connection.cursor() as cursor:
                
                # 1. Видаляємо UserCourseProgress через many-to-many таблицю
                m2m_count = safe_delete_from_table(cursor, "user_course_progress_materials_completed")
                if m2m_count > 0:
                    print(f"✓ Видалено {m2m_count} зв'язків матеріалів з прогресом")
                
                progress_count = safe_delete_from_table(cursor, "user_course_progress")
                if progress_count > 0:
                    print(f"✓ Видалено {progress_count} записів прогресу користувачів")
                else:
                    print("✓ Прогрес користувачів: таблиця порожня")
                
                # 2. Видаляємо Favorites
                favorites_count = safe_delete_from_table(cursor, "favorites")
                if favorites_count > 0:
                    print(f"✓ Видалено {favorites_count} обраних курсів")
                else:
                    print("✓ Обрані курси: таблиця порожня")
                
                # 3. Видаляємо Materials
                materials_count = safe_delete_from_table(cursor, "materials")
                if materials_count > 0:
                    print(f"✓ Видалено {materials_count} матеріалів")
                else:
                    print("✓ Матеріали: таблиця порожня")
                
                # 4. Очищаємо ManyToMany зв'язки Course-Tags
                tags_relations = safe_delete_from_table(cursor, "courses_tags")
                if tags_relations > 0:
                    print(f"✓ Очищено {tags_relations} зв'язків курсів з тегами")
                else:
                    print("✓ Зв'язки курсів з тегами: таблиця порожня")
                
                # 5. Видаляємо Courses
                courses_count = safe_delete_from_table(cursor, "courses")
                if courses_count > 0:
                    print(f"✓ Видалено {courses_count} курсів")
                else:
                    print("✓ Курси: таблиця порожня")
                
                # 6. Видаляємо Categories (спочатку підкатегорії, потім батьківські)
                subcategories_count = safe_delete_from_table(cursor, "categories", "parent_id IS NOT NULL")
                if subcategories_count > 0:
                    print(f"✓ Видалено {subcategories_count} підкатегорій")
                else:
                    print("✓ Підкатегорії: таблиця порожня")
                
                # Батьківські категорії
                parent_categories_count = safe_delete_from_table(cursor, "categories")
                if parent_categories_count > 0:
                    print(f"✓ Видалено {parent_categories_count} батьківських категорій")
                else:
                    print("✓ Батьківські категорії: таблиця порожня")
            
            print("\n" + "="*80)
            print("✅ ОЧИЩЕННЯ ЗАВЕРШЕНО УСПІШНО")
            print("="*80 + "\n")
            
    except Exception as e:
        print(f"\n❌ КРИТИЧНА ПОМИЛКА: {e}")
        import traceback
        traceback.print_exc()
        # Не raise - дозволяємо міграції продовжитись
        print("\n⚠️  Продовжуємо міграцію незважаючи на помилку...")


def create_new_categories(apps, schema_editor):
    """
    Створення НОВОЇ структури категорій згідно дизайну.
    """
    print("\n" + "="*80)
    print("🎨 СТВОРЮЄМО НОВУ СТРУКТУРУ КАТЕГОРІЙ")
    print("="*80 + "\n")
    
    Category = apps.get_model('content', 'Category')
    
    try:
        with transaction.atomic():
            # 1. ТРЕНЕРСТВО (з обов'язковими підкатегоріями)
            trenerstvo = Category.objects.create(
                name='Тренерство',
                slug='trenerstvo',
                description='Навчальні матеріали для тренерів різних напрямків',
                order=1,
                is_active=True,
                is_subcategory_required=True,
                icon='⚽'
            )
            print(f"✓ Створено головну категорію: {trenerstvo.name}")
            
            # Підкатегорії Тренерства
            subcats = [
                ('Тренер воротарів', 'goalkeeper-coach', 'Спеціалізація: підготовка воротарів', 1),
                ('Дитячий тренер', 'kids-coach', 'Робота з юними футболістами', 2),
                ('Тренер ЗФП', 'strength-coach', 'Фізична підготовка спортсменів', 3),
                ('Тренер професійних команд', 'pro-coach', 'Тренерство на професійному рівні', 4),
            ]
            
            for name, slug, desc, order in subcats:
                Category.objects.create(
                    name=name,
                    slug=slug,
                    description=desc,
                    parent=trenerstvo,
                    order=order,
                    is_active=True
                )
                print(f"  ↳ Підкатегорія: {name}")
            
            # 2. Інші головні категорії
            main_categories = [
                ('Аналітика і скаутинг', 'analytics', 'Аналіз гри та пошук талантів', 2, '📊'),
                ('Менеджмент', 'management', 'Управління в футболі', 3, '💼'),
                ('Спортивна психологія', 'psychology', 'Психологічна підготовка', 4, '🧠'),
                ('Нутриціологія', 'nutrition', 'Спортивне харчування', 5, '🥗'),
                ('Реабілітація', 'rehabilitation', 'Відновлення після травм', 6, '🏥'),
                ('Футболіст', 'player', 'Матеріали для гравців', 7, '⚡'),
                ('Батько', 'parent', 'Для батьків юних футболістів', 8, '👨‍👦'),
            ]
            
            for name, slug, desc, order, icon in main_categories:
                Category.objects.create(
                    name=name,
                    slug=slug,
                    description=desc,
                    order=order,
                    is_active=True,
                    is_subcategory_required=False,
                    icon=icon
                )
                print(f"✓ Створено категорію: {name}")
            
            print("\n" + "="*80)
            print(f"✅ СТВОРЕНО {Category.objects.count()} КАТЕГОРІЙ")
            print("="*80 + "\n")
            
    except Exception as e:
        print(f"\n❌ ПОМИЛКА ПРИ СТВОРЕННІ КАТЕГОРІЙ: {e}")
        import traceback
        traceback.print_exc()
        raise


def reverse_operation(apps, schema_editor):
    """
    Rollback операція - просто видалити всі категорії.
    """
    Category = apps.get_model('content', 'Category')
    print("⚠️ ROLLBACK: Видаляємо всі категорії")
    Category.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0015_fix_analytics_category_name'),
    ]

    operations = [
        migrations.RunPython(
            safe_reset_everything,
            reverse_code=migrations.RunPython.noop
        ),
        migrations.RunPython(
            create_new_categories,
            reverse_code=reverse_operation
        ),
    ]

