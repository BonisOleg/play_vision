# Generated manually for SiteSettings model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0010_alter_eventgridcell_image_alter_expertcard_photo_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_auth_url', models.URLField(default='#', help_text='Посилання на зовнішній сайт для входу/реєстрації (наприклад, Квіга)', verbose_name='URL зовнішньої авторизації')),
                ('external_join_url_default', models.URLField(blank=True, help_text='Використовується якщо не вказано в курсі', verbose_name='URL "Приєднатись" за замовчуванням')),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Налаштування сайту',
                'verbose_name_plural': 'Налаштування сайту',
                'db_table': 'cms_site_settings',
            },
        ),
    ]

