# Generated manually to convert AboutSection2 ImageFields to TextFields
# This migration is SAFE because there are no records in the table on production

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0011_add_site_settings'),
    ]

    operations = [
        # Remove old ImageField fields
        migrations.RemoveField(
            model_name='aboutsection2',
            name='image_ua_light',
        ),
        migrations.RemoveField(
            model_name='aboutsection2',
            name='image_ua_dark',
        ),
        migrations.RemoveField(
            model_name='aboutsection2',
            name='image_world_light',
        ),
        migrations.RemoveField(
            model_name='aboutsection2',
            name='image_world_dark',
        ),
        
        # Add new TextField fields
        migrations.AddField(
            model_name='aboutsection2',
            name='image_ua_light',
            field=models.TextField(verbose_name='PNG/SVG UA (світла тема)', default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='aboutsection2',
            name='image_ua_dark',
            field=models.TextField(blank=True, verbose_name='PNG/SVG UA (темна тема)'),
        ),
        migrations.AddField(
            model_name='aboutsection2',
            name='image_world_light',
            field=models.TextField(blank=True, verbose_name='PNG/SVG World (світла)'),
        ),
        migrations.AddField(
            model_name='aboutsection2',
            name='image_world_dark',
            field=models.TextField(blank=True, verbose_name='PNG/SVG World (темна)'),
        ),
    ]

