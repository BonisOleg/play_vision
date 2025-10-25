# Generated migration for Plan improvements

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='plan',
            name='is_best_value',
            field=models.BooleanField(default=False, help_text='Mark as best value (auto-set for longest duration)'),
        ),
        migrations.AddField(
            model_name='plan',
            name='badge_type',
            field=models.CharField(blank=True, choices=[('popular', 'Найпопулярніший'), ('best_value', 'Максимальна економія'), ('recommended', 'Рекомендуємо'), ('new', 'Новинка')], max_length=20),
        ),
        migrations.AddField(
            model_name='plan',
            name='total_subscriptions',
            field=models.PositiveIntegerField(default=0, help_text='Total number of subscriptions sold'),
        ),
        migrations.AlterField(
            model_name='plan',
            name='badge_text',
            field=models.CharField(blank=True, help_text='Custom badge text (optional)', max_length=50),
        ),
        migrations.AlterField(
            model_name='plan',
            name='is_popular',
            field=models.BooleanField(default=False, help_text='Mark as popular plan'),
        ),
    ]

