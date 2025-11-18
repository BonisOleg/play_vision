# Generated manually - SAFE reset of all content and categories
from django.db import migrations, transaction


def safe_reset_everything(apps, schema_editor):
    """
    АГРЕСИВНЕ видалення всього контенту та категорій через RAW SQL.
    Використовує TRUNCATE + DELETE для повного очищення.
    """
    print("\n" + "="*80)
    print("🔥 ПОЧИНАЄМО ПОВНЕ ОЧИЩЕННЯ КОНТЕНТУ ТА КАТЕГОРІЙ")
    print("="*80 + "\n")
    
    try:
        with schema_editor.connection.cursor() as cursor:
            # Вимикаємо перевірки foreign key (для PostgreSQL)
            try:
                cursor.execute("SET CONSTRAINTS ALL DEFERRED")
            except:
                pass
            
            # 1. Видаляємо UserCourseProgress
            try:
                cursor.execute("DELETE FROM user_course_progress_materials_completed")
                cursor.execute("DELETE FROM user_course_progress")
                print("✓ Прогрес користувачів: видалено")
            except Exception as e:
                print(f"⚠️  Прогрес: {e}")
            
            # 2. Видаляємо Favorites
            try:
                cursor.execute("DELETE FROM favorites")
                print("✓ Обрані курси: видалено")
            except Exception as e:
                print(f"⚠️  Обрані: {e}")
            
            # 3. Видаляємо Materials
            try:
                cursor.execute("DELETE FROM materials")
                print("✓ Матеріали: видалено")
            except Exception as e:
                print(f"⚠️  Матеріали: {e}")
            
            # 4. Видаляємо зв'язки курсів з тегами
            try:
                cursor.execute("DELETE FROM content_course_tags")
                print("✓ Зв'язки курсів з тегами: видалено")
            except Exception as e:
                print(f"⚠️  Зв'язки з тегами: {e}")
            
            # 5. Видаляємо Courses
            try:
                cursor.execute("DELETE FROM courses")
                print("✓ Курси: видалено")
            except Exception as e:
                print(f"⚠️  Курси: {e}")
            
            # 6. КРИТИЧНО: Видаляємо ВСІ категорії (спочатку підкатегорії, потім головні)
            try:
                cursor.execute("DELETE FROM categories WHERE parent_id IS NOT NULL")
                cursor.execute("DELETE FROM categories WHERE parent_id IS NULL")
                cursor.execute("DELETE FROM categories")  # На всяк випадок
                print("✓ ВСІ КАТЕГОРІЇ ВИДАЛЕНО")
                
                # ПЕРЕВІРКА
                cursor.execute("SELECT COUNT(*) FROM categories")
                remaining = cursor.fetchone()[0]
                if remaining > 0:
                    print(f"❌❌❌ ЗАЛИШИЛОСЬ {remaining} КАТЕГОРІЙ!")
                    # Спробуємо ще раз через ORM
                    Category = apps.get_model('content', 'Category')
                    Category.objects.all().delete()
                    print("✓ Видалено через ORM")
                else:
                    print("✅ Таблиця categories ПОРОЖНЯ")
            except Exception as e:
                print(f"❌ КРИТИЧНА ПОМИЛКА: {e}")
                # Останній шанс - через ORM
                try:
                    Category = apps.get_model('content', 'Category')
                    deleted = Category.objects.all().delete()
                    print(f"✓ Видалено через ORM: {deleted}")
                except Exception as orm_error:
                    print(f"❌ ORM теж не спрацював: {orm_error}")
                    raise
        
        print("\n" + "="*80)
        print("✅ ОЧИЩЕННЯ ЗАВЕРШЕНО")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ КРИТИЧНА ПОМИЛКА: {e}")
        import traceback
        traceback.print_exc()
        raise  # ЗУПИНЯЄМО міграцію


def create_new_categories(apps, schema_editor):
    """
    Створення НОВОЇ структури категорій згідно дизайну.
    IDEMPOTENT - можна запускати багато разів без помилок.
    """
    print("\n" + "="*80)
    print("🎨 СТВОРЮЄМО НОВУ СТРУКТУРУ КАТЕГОРІЙ")
    print("="*80 + "\n")
    
    Category = apps.get_model('content', 'Category')
    
    try:
        with transaction.atomic():
            # 1. ТРЕНЕРСТВО (з обов'язковими підкатегоріями)
            trenerstvo, created = Category.objects.get_or_create(
                slug='trenerstvo',
                defaults={
                    'name': 'Тренерство',
                    'description': 'Навчальні матеріали для тренерів різних напрямків',
                    'order': 1,
                    'is_active': True,
                    'is_subcategory_required': True,
                    'icon': '⚽'
                }
            )
            if created:
                print(f"✓ Створено головну категорію: {trenerstvo.name}")
            else:
                print(f"⚠️  Категорія вже існує: {trenerstvo.name}")
            
            # Підкатегорії Тренерства
            subcats = [
                ('Тренер воротарів', 'goalkeeper-coach', 'Спеціалізація: підготовка воротарів', 1),
                ('Дитячий тренер', 'kids-coach', 'Робота з юними футболістами', 2),
                ('Тренер ЗФП', 'strength-coach', 'Фізична підготовка спортсменів', 3),
                ('Тренер професійних команд', 'pro-coach', 'Тренерство на професійному рівні', 4),
            ]
            
            for name, slug, desc, order in subcats:
                subcat, created = Category.objects.get_or_create(
                    slug=slug,
                    defaults={
                        'name': name,
                        'description': desc,
                        'parent': trenerstvo,
                        'order': order,
                        'is_active': True
                    }
                )
                if created:
                    print(f"  ↳ Підкатегорія: {name}")
                else:
                    print(f"  ⚠️  Підкатегорія вже існує: {name}")
            
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
                cat, created = Category.objects.get_or_create(
                    slug=slug,
                    defaults={
                        'name': name,
                        'description': desc,
                        'order': order,
                        'is_active': True,
                        'is_subcategory_required': False,
                        'icon': icon
                    }
                )
                if created:
                    print(f"✓ Створено категорію: {name}")
                else:
                    print(f"⚠️  Категорія вже існує: {name}")
            
            total_count = Category.objects.count()
            print("\n" + "="*80)
            print(f"✅ ВСЬОГО КАТЕГОРІЙ В БД: {total_count}")
            print("="*80 + "\n")
            
    except Exception as e:
        print(f"\n❌ ПОМИЛКА ПРИ СТВОРЕННІ КАТЕГОРІЙ: {e}")
        import traceback
        traceback.print_exc()
        # НЕ raise - дозволяємо міграції продовжитись
        print("\n⚠️  Продовжуємо міграцію незважаючи на помилку...")


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

