# Generated manually for badge fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0005_add_author_and_target_audience'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='badge_type',
            field=models.CharField(
                choices=[
                    ('none', 'Без бейджа'),
                    ('bestseller', 'Топ-продажів'),
                    ('new', 'Новинка'),
                    ('recommended', 'Для вас'),
                    ('classic', 'Вічна класика'),
                ],
                db_index=True,
                default='none',
                help_text='Оберіть бейдж для відображення на картці курсу',
                max_length=20,
                verbose_name='Тип бейджа'
            ),
        ),
        migrations.AddField(
            model_name='course',
            name='is_classic',
            field=models.BooleanField(
                default=False,
                help_text='Позначити курс як класичний/вічний контент',
                verbose_name='Вічна класика'
            ),
        ),
    ]

