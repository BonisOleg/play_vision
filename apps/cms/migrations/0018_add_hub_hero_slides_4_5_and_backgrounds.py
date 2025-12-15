# Generated manually
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0017_add_grid_svg_fields'),
    ]

    operations = [
        # Зробити background_image optional для зворотної сумісності
        migrations.AlterField(
            model_name='hubhero',
            name='background_image',
            field=models.ImageField(
                blank=True,
                help_text='Використовується як fallback, якщо для слайда не вказано окремий бекграунд',
                max_length=500,
                upload_to='cms/hub/hero/',
                verbose_name='Фонове зображення (загальне)'
            ),
        ),
        # Додати бекграунди для слайда 1
        migrations.AddField(
            model_name='hubhero',
            name='background_image_1',
            field=models.ImageField(
                blank=True,
                help_text='Рекомендовано: 1920×1080 px',
                max_length=500,
                upload_to='cms/hub/hero/',
                verbose_name='Бекграунд зображення 1'
            ),
        ),
        migrations.AddField(
            model_name='hubhero',
            name='background_video_1',
            field=models.FileField(
                blank=True,
                help_text='MP4 формат',
                max_length=500,
                upload_to='cms/hub/hero/videos/',
                verbose_name='Бекграунд відео 1'
            ),
        ),
        # Додати бекграунди для слайда 2
        migrations.AddField(
            model_name='hubhero',
            name='background_image_2',
            field=models.ImageField(
                blank=True,
                help_text='Рекомендовано: 1920×1080 px',
                max_length=500,
                upload_to='cms/hub/hero/',
                verbose_name='Бекграунд зображення 2'
            ),
        ),
        migrations.AddField(
            model_name='hubhero',
            name='background_video_2',
            field=models.FileField(
                blank=True,
                help_text='MP4 формат',
                max_length=500,
                upload_to='cms/hub/hero/videos/',
                verbose_name='Бекграунд відео 2'
            ),
        ),
        # Додати бекграунди для слайда 3
        migrations.AddField(
            model_name='hubhero',
            name='background_image_3',
            field=models.ImageField(
                blank=True,
                help_text='Рекомендовано: 1920×1080 px',
                max_length=500,
                upload_to='cms/hub/hero/',
                verbose_name='Бекграунд зображення 3'
            ),
        ),
        migrations.AddField(
            model_name='hubhero',
            name='background_video_3',
            field=models.FileField(
                blank=True,
                help_text='MP4 формат',
                max_length=500,
                upload_to='cms/hub/hero/videos/',
                verbose_name='Бекграунд відео 3'
            ),
        ),
        # Додати слайд 4
        migrations.AddField(
            model_name='hubhero',
            name='title_4_ua',
            field=models.CharField(blank=True, max_length=200, verbose_name='Заголовок 4 (Україна)'),
        ),
        migrations.AddField(
            model_name='hubhero',
            name='subtitle_4_ua',
            field=models.CharField(blank=True, max_length=300, verbose_name='Підзаголовок 4 (Україна)'),
        ),
        migrations.AddField(
            model_name='hubhero',
            name='title_4_world',
            field=models.CharField(blank=True, max_length=200, verbose_name='Заголовок 4 (Світ)'),
        ),
        migrations.AddField(
            model_name='hubhero',
            name='subtitle_4_world',
            field=models.CharField(blank=True, max_length=300, verbose_name='Підзаголовок 4 (Світ)'),
        ),
        migrations.AddField(
            model_name='hubhero',
            name='background_image_4',
            field=models.ImageField(
                blank=True,
                help_text='Рекомендовано: 1920×1080 px',
                max_length=500,
                upload_to='cms/hub/hero/',
                verbose_name='Бекграунд зображення 4'
            ),
        ),
        migrations.AddField(
            model_name='hubhero',
            name='background_video_4',
            field=models.FileField(
                blank=True,
                help_text='MP4 формат',
                max_length=500,
                upload_to='cms/hub/hero/videos/',
                verbose_name='Бекграунд відео 4'
            ),
        ),
        # Додати слайд 5
        migrations.AddField(
            model_name='hubhero',
            name='title_5_ua',
            field=models.CharField(blank=True, max_length=200, verbose_name='Заголовок 5 (Україна)'),
        ),
        migrations.AddField(
            model_name='hubhero',
            name='subtitle_5_ua',
            field=models.CharField(blank=True, max_length=300, verbose_name='Підзаголовок 5 (Україна)'),
        ),
        migrations.AddField(
            model_name='hubhero',
            name='title_5_world',
            field=models.CharField(blank=True, max_length=200, verbose_name='Заголовок 5 (Світ)'),
        ),
        migrations.AddField(
            model_name='hubhero',
            name='subtitle_5_world',
            field=models.CharField(blank=True, max_length=300, verbose_name='Підзаголовок 5 (Світ)'),
        ),
        migrations.AddField(
            model_name='hubhero',
            name='background_image_5',
            field=models.ImageField(
                blank=True,
                help_text='Рекомендовано: 1920×1080 px',
                max_length=500,
                upload_to='cms/hub/hero/',
                verbose_name='Бекграунд зображення 5'
            ),
        ),
        migrations.AddField(
            model_name='hubhero',
            name='background_video_5',
            field=models.FileField(
                blank=True,
                help_text='MP4 формат',
                max_length=500,
                upload_to='cms/hub/hero/videos/',
                verbose_name='Бекграунд відео 5'
            ),
        ),
    ]

