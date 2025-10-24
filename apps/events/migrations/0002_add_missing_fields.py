# Generated manually for production sync

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        # Add requires_subscription if not exists
        migrations.AddField(
            model_name='event',
            name='requires_subscription',
            field=models.BooleanField(
                default=False,
                help_text='Чи можна використати квитки з підписки'
            ),
        ),
    ]

