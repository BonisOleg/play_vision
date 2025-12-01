# Generated migration for adding video fields to Event

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0014_add_experts_to_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='video_enabled',
            field=models.BooleanField(default=False, help_text='Показати відео замість зображення', verbose_name='Відео увімкнено'),
        ),
        migrations.AddField(
            model_name='event',
            name='video_library_id_ua',
            field=models.CharField(blank=True, help_text='ID бібліотеки BunnyNet (напр. "123456")', max_length=100, verbose_name='BunnyNet Library ID (Україна)'),
        ),
        migrations.AddField(
            model_name='event',
            name='video_id_ua',
            field=models.CharField(blank=True, help_text='ID відео в BunnyNet (напр. "abc123-def456")', max_length=100, verbose_name='BunnyNet Video ID (Україна)'),
        ),
        migrations.AddField(
            model_name='event',
            name='video_library_id_world',
            field=models.CharField(blank=True, help_text='Залиште порожнім щоб використовувати українську версію', max_length=100, verbose_name='BunnyNet Library ID (Світ)'),
        ),
        migrations.AddField(
            model_name='event',
            name='video_id_world',
            field=models.CharField(blank=True, help_text='Залиште порожнім щоб використовувати українську версію', max_length=100, verbose_name='BunnyNet Video ID (Світ)'),
        ),
    ]

