# Generated manually for Bunny.net integration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0006_add_badge_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='video_source',
            field=models.CharField(
                choices=[
                    ('local', 'Локальне зберігання'),
                    ('s3', 'AWS S3'),
                    ('bunny', 'Bunny.net CDN')
                ],
                default='local',
                help_text='Джерело відео',
                max_length=20,
                db_index=True
            ),
        ),
        migrations.AddField(
            model_name='material',
            name='bunny_video_id',
            field=models.CharField(
                blank=True,
                help_text='GUID відео в Bunny.net',
                max_length=100,
                db_index=True
            ),
        ),
        migrations.AddField(
            model_name='material',
            name='bunny_collection_id',
            field=models.CharField(
                blank=True,
                help_text='ID колекції в Bunny.net',
                max_length=100
            ),
        ),
        migrations.AddField(
            model_name='material',
            name='bunny_video_status',
            field=models.CharField(
                blank=True,
                help_text='Статус обробки відео в Bunny.net (0-6)',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='material',
            name='bunny_thumbnail_url',
            field=models.URLField(
                blank=True,
                help_text='URL thumbnail з Bunny.net'
            ),
        ),
    ]

