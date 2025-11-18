# Generated manually - SAFE reset of all content and categories
from django.db import migrations, transaction
from django.db.models import Q


def safe_reset_everything(apps, schema_editor):
    """
    БЕЗПЕЧНЕ видалення всього контенту та категорій.
    Працює на будь-якій БД (PostgreSQL, SQLite).
    """
    print("\n" + "="*80)
    print("🔥 ПОЧИНАЄМО ПОВНЕ ОЧИЩЕННЯ КОНТЕНТУ ТА КАТЕГОРІЙ")
    print("="*80 + "\n")
    
    # Отримуємо моделі
    Course = apps.get_model('content', 'Course')
    Category = apps.get_model('content', 'Category')
    Material = apps.get_model('content', 'Material')
    UserCourseProgress = apps.get_model('content', 'UserCourseProgress')
    Favorite = apps.get_model('content', 'Favorite')
    Tag = apps.get_model('content', 'Tag')
    
    try:
        with transaction.atomic():
            # 1. Видаляємо UserCourseProgress (залежить від Course і Material)
            progress_count = UserCourseProgress.objects.count()
            if progress_count > 0:
                UserCourseProgress.objects.all().delete()
                print(f"✓ Видалено {progress_count} записів прогресу користувачів")
            else:
                print("✓ Прогрес користувачів: таблиця порожня")
            
            # 2. Видаляємо Favorites (залежить від Course)
            favorites_count = Favorite.objects.count()
            if favorites_count > 0:
                Favorite.objects.all().delete()
                print(f"✓ Видалено {favorites_count} обраних курсів")
            else:
                print("✓ Обрані курси: таблиця порожня")
            
            # 3. Видаляємо Materials (залежить від Course)
            materials_count = Material.objects.count()
            if materials_count > 0:
                Material.objects.all().delete()
                print(f"✓ Видалено {materials_count} матеріалів")
            else:
                print("✓ Матеріали: таблиця порожня")
            
            # 4. Видаляємо всі зв'язки Course-Tags через ManyToMany
            for course in Course.objects.all():
                course.tags.clear()
            print("✓ Очищено всі зв'язки курсів з тегами")
            
            # 5. Видаляємо Courses (залежить від Category)
            courses_count = Course.objects.count()
            if courses_count > 0:
                Course.objects.all().delete()
                print(f"✓ Видалено {courses_count} курсів")
            else:
                print("✓ Курси: таблиця порожня")
            
            # 6. Видаляємо Categories (спочатку підкатегорії, потім батьківські)
            # Підкатегорії (ті що мають parent)
            subcategories_count = Category.objects.filter(parent__isnull=False).count()
            if subcategories_count > 0:
                Category.objects.filter(parent__isnull=False).delete()
                print(f"✓ Видалено {subcategories_count} підкатегорій")
            else:
                print("✓ Підкатегорії: таблиця порожня")
            
            # Батьківські категорії
            parent_categories_count = Category.objects.count()
            if parent_categories_count > 0:
                Category.objects.all().delete()
                print(f"✓ Видалено {parent_categories_count} батьківських категорій")
            else:
                print("✓ Батьківські категорії: таблиця порожня")
            
            print("\n" + "="*80)
            print("✅ ОЧИЩЕННЯ ЗАВЕРШЕНО УСПІШНО")
            print("="*80 + "\n")
            
    except Exception as e:
        print(f"\n❌ ПОМИЛКА ПРИ ОЧИЩЕННІ: {e}")
        import traceback
        traceback.print_exc()
        raise


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

