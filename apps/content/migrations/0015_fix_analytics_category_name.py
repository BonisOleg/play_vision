# Generated manually to fix Analytics category name
from django.db import migrations


def fix_analytics_name(apps, schema_editor):
    """Змінити 'Аналітика та скаутинг' на 'Аналітика і скаутинг'"""
    Category = apps.get_model('content', 'Category')
    try:
        analytics = Category.objects.get(slug='analytics')
        analytics.name = 'Аналітика і скаутинг'
        analytics.save(update_fields=['name'])
    except Category.DoesNotExist:
        pass


def reverse_analytics_name(apps, schema_editor):
    """Повернути назву назад"""
    Category = apps.get_model('content', 'Category')
    try:
        analytics = Category.objects.get(slug='analytics')
        analytics.name = 'Аналітика та скаутинг'
        analytics.save(update_fields=['name'])
    except Category.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0012_populate_new_categories'),
    ]

    operations = [
        migrations.RunPython(fix_analytics_name, reverse_analytics_name),
    ]

