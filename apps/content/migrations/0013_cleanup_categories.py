# Generated manually - cleanup wrong categories

from django.db import migrations


def cleanup_categories(apps, schema_editor):
    """Видалення старих неправильних категорій"""
    Category = apps.get_model('content', 'Category')
    
    # Видалити всі категорії які НЕ є в правильному списку
    valid_slugs = [
        'trenerstvo',
        'coach-gk',
        'coach-youth',
        'coach-fitness',
        'coach-pro',
        'analytics',
        'management',
        'psychology',
        'nutrition',
        'rehabilitation',
        'player',
        'parent'
    ]
    
    Category.objects.exclude(slug__in=valid_slugs).delete()
    
    # Оновити назви якщо вони неправильні
    updates = {
        'analytics': 'Аналітика та скаутинг',
        'psychology': 'Спортивна психологія',
        'nutrition': 'Нутриціологія',
        'player': 'Футболіст',
    }
    
    for slug, name in updates.items():
        Category.objects.filter(slug=slug).update(name=name)


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0012_populate_new_categories'),
    ]

    operations = [
        migrations.RunPython(cleanup_categories, migrations.RunPython.noop),
    ]

