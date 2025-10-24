# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_add_event_details_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='event_category',
            field=models.CharField(
                blank=True,
                choices=[
                    ('football_experts_forum', 'Форум футбольних фахівців'),
                    ('parents_forum', 'Форум футбольних батьків'),
                    ('internships', 'Стажування в професійних клубах'),
                    ('seminars_hackathons', 'Практичні семінари і хакатони'),
                    ('psychology_workshops', 'Воркшопи зі спортивної психології'),
                    ('selection_camps', 'Селекційні табори'),
                    ('online_webinars', 'Онлайн-теорії і вебінари'),
                ],
                help_text='Специфічна категорія події для меню',
                max_length=50,
            ),
        ),
    ]

