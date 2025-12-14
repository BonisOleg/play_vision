# Generated migration for subscription_text field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0015_add_course_badges_and_discounts'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='subscription_text',
            field=models.CharField(
                blank=True,
                help_text='Кастомний текст, який відображається на картці курсу коли галочка "Доступно за підпискою" не обрана',
                max_length=200,
                null=True,
                verbose_name='Текст про підписку'
            ),
        ),
    ]
