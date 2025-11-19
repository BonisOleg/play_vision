from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0007_remove_eventregistration_event_registrations_user_status_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventticket',
            name='tier_name',
            field=models.CharField(blank=True, help_text='Назва тарифу (Базовий, ПРО, Преміум)', max_length=50),
        ),
        migrations.AlterField(
            model_name='event',
            name='ticket_tiers',
            field=models.JSONField(blank=True, default=list, help_text='Тарифи квитків: [{"name": "Базовий", "price": 350, "features": ["пункт 1", "..."], "is_popular": false}]', verbose_name='Тарифи квитків'),
        ),
    ]

