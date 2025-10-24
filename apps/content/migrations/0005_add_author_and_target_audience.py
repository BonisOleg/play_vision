# Generated manually for new Course fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0004_populate_user_interests'),
    ]

    operations = [
        # Додати поле author до Course
        migrations.AddField(
            model_name='course',
            name='author',
            field=models.CharField(
                blank=True,
                help_text="Ім'я автора/інструктора курсу",
                max_length=200,
                verbose_name='Автор курсу'
            ),
        ),
        
        # Додати choices для content_type
        migrations.AddField(
            model_name='course',
            name='content_type',
            field=models.CharField(
                choices=[
                    ('video', 'Відео'),
                    ('pdf', 'PDF документ'),
                    ('article', 'Стаття'),
                    ('mixed', 'Змішаний'),
                ],
                default='mixed',
                help_text='Основний тип матеріалів у курсі',
                max_length=20,
                verbose_name='Тип контенту',
                db_index=True
            ),
        ),
        
        # Додати поле target_audience до Course
        migrations.AddField(
            model_name='course',
            name='target_audience',
            field=models.JSONField(
                blank=True,
                default=list,
                help_text='Список цільових аудиторій (можна обрати декілька)',
                verbose_name='Кому підходить'
            ),
        ),
    ]

