# Generated manually to remove Event.tags field
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0007_remove_eventregistration_event_registrations_user_status_idx_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='tags',
        ),
    ]

