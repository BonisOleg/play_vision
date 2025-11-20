# Generated manually for course promo video fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0013_remove_category_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='promo_video_file',
            field=models.FileField(blank=True, help_text='Завантажте відео - воно автоматично піде на Bunny.net CDN', max_length=500, null=True, upload_to='course_promo_temp/', verbose_name='Промо-відео (тимчасове)'),
        ),
        migrations.AddField(
            model_name='course',
            name='promo_video_bunny_id',
            field=models.CharField(blank=True, db_index=True, help_text='GUID відео в Bunny.net (заповнюється автоматично)', max_length=100, verbose_name='Bunny Video ID'),
        ),
        migrations.AddField(
            model_name='course',
            name='promo_video_bunny_status',
            field=models.CharField(blank=True, help_text='Статус обробки відео (0-6)', max_length=20, verbose_name='Bunny статус'),
        ),
        migrations.AddField(
            model_name='course',
            name='promo_video_thumbnail_url',
            field=models.URLField(blank=True, help_text='URL thumbnail з Bunny.net', verbose_name='Thumbnail URL'),
        ),
        migrations.AddField(
            model_name='course',
            name='external_join_url',
            field=models.URLField(blank=True, help_text='URL зовнішнього сайту для кнопки "Приєднатись до клубу"', verbose_name='Посилання "Приєднатись"'),
        ),
    ]

