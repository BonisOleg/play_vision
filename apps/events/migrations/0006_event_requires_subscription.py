# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_update_speaker_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='requires_subscription',
            field=models.BooleanField(
                default=False,
                help_text='Чи можна використати квитки з підписки'
            ),
        ),
    ]

