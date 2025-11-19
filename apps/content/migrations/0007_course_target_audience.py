from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0010_rename_monthly_quotes_month_active_idx_monthly_quo_month_cc6c8a_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='target_audience',
            field=models.JSONField(blank=True, default=list, help_text='Виберіть цільову аудиторію курсу', verbose_name='Кому підходить'),
        ),
    ]

