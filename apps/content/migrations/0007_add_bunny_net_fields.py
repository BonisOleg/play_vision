# Dummy migration - already applied on Render
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('content', '0006_add_badge_fields'),
    ]
    operations = []

