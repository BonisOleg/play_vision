# Generated manually - reset categories and courses
from django.db import migrations


def reset_categories(apps, schema_editor):
    """Видалити всі курси та категорії, створити правильні категорії зі скріншоту"""
    Category = apps.get_model('content', 'Category')
    Course = apps.get_model('content', 'Course')
    
    # Видалити всі курси
    Course.objects.all().delete()
    print("✓ Видалено всі курси")
    
    # Видалити всі категорії
    Category.objects.all().delete()
    print("✓ Видалено всі категорії")
    
    # Створити Тренерство з підкатегоріями
    trenerstvo = Category.objects.create(
        name='Тренерство',
        slug='trenerstvo',
        description='Курси для тренерів',
        order=1,
        is_active=True,
        is_subcategory_required=True
    )
    
    # Підкатегорії Тренерства (як на скріншоті)
    Category.objects.create(
        name='Тренер воротарів',
        slug='goalkeeper-coach',
        parent=trenerstvo,
        order=1,
        is_active=True
    )
    Category.objects.create(
        name='Дитячий тренер',
        slug='kids-coach',
        parent=trenerstvo,
        order=2,
        is_active=True
    )
    Category.objects.create(
        name='Тренер ЗФП',
        slug='strength-coach',
        parent=trenerstvo,
        order=3,
        is_active=True
    )
    Category.objects.create(
        name='Тренер професійних команд',
        slug='pro-coach',
        parent=trenerstvo,
        order=4,
        is_active=True
    )
    print("✓ Створено Тренерство з підкатегоріями")
    
    # Інші категорії (як на скріншоті)
    Category.objects.create(
        name='Аналітика і скаутинг',
        slug='analytics',
        description='Аналітика та скаутинг',
        order=2,
        is_active=True
    )
    Category.objects.create(
        name='Менеджмент',
        slug='management',
        description='Менеджмент в спорті',
        order=3,
        is_active=True
    )
    Category.objects.create(
        name='Спортивна психологія',
        slug='sports-psychology',
        description='Спортивна психологія',
        order=4,
        is_active=True
    )
    Category.objects.create(
        name='Нутриціологія',
        slug='nutrition',
        description='Спортивна нутриціологія',
        order=5,
        is_active=True
    )
    Category.objects.create(
        name='Реабілітація',
        slug='rehabilitation',
        description='Спортивна реабілітація',
        order=6,
        is_active=True
    )
    Category.objects.create(
        name='Футболіст',
        slug='player',
        description='Курси для футболістів',
        order=7,
        is_active=True
    )
    Category.objects.create(
        name='Батько',
        slug='parent',
        description='Курси для батьків',
        order=8,
        is_active=True
    )
    print("✓ Створено всі категорії зі скріншоту")


def reverse_reset(apps, schema_editor):
    """Reverse operation - just pass"""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0015_fix_analytics_category_name'),
    ]

    operations = [
        migrations.RunPython(reset_categories, reverse_reset),
    ]

