# Generated manually for phone registration features

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        # Make email nullable and unique
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField('email address', unique=True, blank=True, null=True),
        ),
        # Make phone unique and nullable
        migrations.AlterField(
            model_name='user',
            name='phone',
            field=models.CharField(max_length=20, blank=True, unique=True, null=True, help_text='Phone number in international format'),
        ),
        # Add phone registration date field
        migrations.AddField(
            model_name='user',
            name='phone_registered_at',
            field=models.DateTimeField(null=True, blank=True, help_text='Date when user registered with phone only'),
        ),
    ]
