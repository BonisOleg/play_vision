# Data migration для створення 8 інтересів користувачів
from django.db import migrations


def create_user_interests(apps, schema_editor):
    """
    Створити 8 інтересів у правильному порядку
    """
    Tag = apps.get_model('content', 'Tag')
    
    # Видалити старі інтереси якщо є
    Tag.objects.filter(tag_type='interest').delete()
    
    # Створити 8 інтересів у правильному порядку
    interests = [
        (1, 'training', 'Тренерство'),
        (2, 'analytics', 'Аналітика і скаутинг'),
        (3, 'fitness', 'ЗФП'),
        (4, 'management', 'Менеджмент'),
        (5, 'psychology', 'Психологія'),
        (6, 'nutrition', 'Нутриціологія'),
        (7, 'player', 'Футболіст'),
        (8, 'parent', 'Батько'),
    ]
    
    for order, slug, name in interests:
        Tag.objects.create(
            name=name,
            slug=slug,
            tag_type='interest',
            display_order=order
        )
    
    print(f"✅ Створено {len(interests)} інтересів користувачів")


def reverse_migration(apps, schema_editor):
    """Відкат міграції"""
    Tag = apps.get_model('content', 'Tag')
    Tag.objects.filter(tag_type='interest').delete()


class Migration(migrations.Migration):
    
    dependencies = [
        ('content', '0003_add_tag_fields_and_monthly_quote'),
    ]
    
    operations = [
        migrations.RunPython(create_user_interests, reverse_migration),
    ]

