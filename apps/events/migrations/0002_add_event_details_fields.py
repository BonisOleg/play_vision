# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='benefits',
            field=models.JSONField(blank=True, default=list, help_text='Список переваг події (що отримає учасник)', verbose_name='Що ти отримаєш'),
        ),
        migrations.AddField(
            model_name='event',
            name='target_audience',
            field=models.JSONField(blank=True, default=list, help_text='Для кого ця подія (цільова аудиторія)', verbose_name='Для кого'),
        ),
        migrations.AddField(
            model_name='event',
            name='ticket_tiers',
            field=models.JSONField(blank=True, default=list, help_text='Тарифи квитків у форматі JSON: [{"name": "STANDARD", "price": 5450, "features": ["..."]}]', verbose_name='Тарифи квитків'),
        ),
    ]

