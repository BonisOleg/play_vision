# Generated migration for course badges and discounts

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0014_add_promo_video_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='has_discount',
            field=models.BooleanField(default=False, db_index=True, help_text='Активувати знижку для цього курсу', verbose_name='Знижка активна'),
        ),
        migrations.AddField(
            model_name='course',
            name='discount_percent',
            field=models.PositiveIntegerField(default=0, help_text='Вкажіть відсоток знижки (1-99%)', verbose_name='Відсоток знижки'),
        ),
        migrations.AddField(
            model_name='course',
            name='is_top_seller',
            field=models.BooleanField(default=False, db_index=True, help_text='Показати бейдж "Топ продажів"', verbose_name='Топ продажів'),
        ),
    ]
