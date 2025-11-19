# Generated manually to remove Category and Tag models and course.category field
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0010_rename_monthly_quotes_month_active_idx_monthly_quo_month_cc6c8a_idx_and_more'),
    ]

    operations = [
        # Видалити поле category з Course
        migrations.RemoveField(
            model_name='course',
            name='category',
        ),
        
        # Видалити моделі Category та Tag
        migrations.DeleteModel(
            name='Category',
        ),
        migrations.DeleteModel(
            name='Tag',
        ),
    ]

