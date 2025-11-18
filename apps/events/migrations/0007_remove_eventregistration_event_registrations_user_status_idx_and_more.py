# Dummy migration - already applied on Render
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('events', '0006_eventfeedback_eventwaitlist_and_more'),
    ]
    operations = []

