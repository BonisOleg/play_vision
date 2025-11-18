# Generated manually for adding course logo field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0006_add_badge_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='logo',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='course_logos/',
                verbose_name='Лого курсу',
                help_text='Квадратне лого курсу для відображення на картці (рекомендовано 200x200px)'
            ),
        ),
    ]

