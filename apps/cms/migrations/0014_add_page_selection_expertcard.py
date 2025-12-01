# Generated migration for adding page selection to ExpertCard

from django.db import migrations, models


def migrate_show_on_homepage_to_show_on_home(apps, schema_editor):
    """Перенести дані з show_on_homepage до show_on_home"""
    ExpertCard = apps.get_model('cms', 'ExpertCard')
    for expert in ExpertCard.objects.all():
        expert.show_on_home = expert.show_on_homepage
        expert.order_home = expert.order
        expert.save()


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0013_add_video_to_about_hero'),
        ('events', '0011_make_event_fields_optional'),
    ]

    operations = [
        # 1. Додати нові поля для show_on
        migrations.AddField(
            model_name='expertcard',
            name='show_on_home',
            field=models.BooleanField(default=False, verbose_name='Показувати на головній'),
        ),
        migrations.AddField(
            model_name='expertcard',
            name='show_on_about',
            field=models.BooleanField(default=False, verbose_name='Показувати на "Про нас"'),
        ),
        migrations.AddField(
            model_name='expertcard',
            name='show_on_mentoring',
            field=models.BooleanField(default=False, verbose_name='Показувати на "Ментор коучинг"'),
        ),
        # 2. Додати нові поля для порядку
        migrations.AddField(
            model_name='expertcard',
            name='order_home',
            field=models.PositiveIntegerField(default=0, verbose_name='Порядок на головній'),
        ),
        migrations.AddField(
            model_name='expertcard',
            name='order_about',
            field=models.PositiveIntegerField(default=0, verbose_name='Порядок на "Про нас"'),
        ),
        migrations.AddField(
            model_name='expertcard',
            name='order_mentoring',
            field=models.PositiveIntegerField(default=0, verbose_name='Порядок на "Ментор коучинг"'),
        ),
        # 3. Міграція даних
        migrations.RunPython(migrate_show_on_homepage_to_show_on_home),
        # 4. Видалити старе поле
        migrations.RemoveField(
            model_name='expertcard',
            name='show_on_homepage',
        ),
    ]

