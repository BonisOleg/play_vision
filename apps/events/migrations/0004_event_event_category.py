# Dummy migration - already applied on Render
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('events', '0003_add_event_details_fields'),
    ]
    operations = []

