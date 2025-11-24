# Generated migration for landing app

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LeadSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(help_text="Ім'я та прізвище учасника", max_length=255, verbose_name="Повне ім'я")),
                ('phone', models.CharField(help_text='Український мобільний номер у форматі +380XXXXXXXXX', max_length=20, validators=[django.core.validators.RegexValidator(message='Номер телефону має бути у форматі +380XXXXXXXXX', regex='^\\+380\\d{9}$')], verbose_name='Телефон')),
                ('email', models.EmailField(help_text='Електронна адреса учасника', max_length=254, verbose_name='Email')),
                ('promo_code', models.CharField(blank=True, default='', help_text="Промокод для знижки (необов'язково)", max_length=50, verbose_name='Промокод')),
                ('submitted_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата подання')),
                ('sendpulse_synced', models.BooleanField(default=False, help_text='Чи відправлено контакт в SendPulse CRM', verbose_name='Синхронізовано з SendPulse')),
                ('sendpulse_contact_id', models.CharField(blank=True, default='', help_text='ID контакту в SendPulse CRM', max_length=100, verbose_name='ID контакту в SendPulse')),
            ],
            options={
                'verbose_name': 'Заявка з Landing Page',
                'verbose_name_plural': 'Заявки з Landing Page',
                'ordering': ['-submitted_at'],
            },
        ),
    ]

