# Generated migration for adding source field to LeadSubmission

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0002_rename_full_name_to_first_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='leadsubmission',
            name='source',
            field=models.CharField(
                choices=[
                    ('landing', 'Landing Page'),
                    ('hub', 'Хаб знань'),
                    ('mentoring', 'Ментор-коучинг'),
                    ('subscription', 'Підписка'),
                ],
                default='landing',
                help_text='Джерело, з якого прийшла заявка',
                max_length=50,
                verbose_name='Джерело заявки',
            ),
        ),
    ]

