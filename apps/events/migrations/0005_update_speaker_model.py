# Dummy migration - already applied on Render
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('events', '0004_event_event_category'),
    ]
    operations = []

