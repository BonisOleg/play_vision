# Generated manually to fix Event model fields
from django.db import migrations, models
import django.core.validators
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0010_alter_event_banner_image_alter_event_thumbnail_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Зробити start_datetime та end_datetime nullable
        migrations.AlterField(
            model_name='event',
            name='start_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='end_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        # Зробити location nullable
        migrations.AlterField(
            model_name='event',
            name='location',
            field=models.CharField(blank=True, max_length=200, help_text='Фізична адреса або "Онлайн"'),
        ),
        # Додати default до price
        migrations.AlterField(
            model_name='event',
            name='price',
            field=models.DecimalField(
                decimal_places=2, 
                default=0, 
                max_digits=10, 
                validators=[django.core.validators.MinValueValidator(0)]
            ),
        ),
        # Зробити organizer nullable
        migrations.AlterField(
            model_name='event',
            name='organizer',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='organized_events',
                to=settings.AUTH_USER_MODEL
            ),
        ),
    ]

