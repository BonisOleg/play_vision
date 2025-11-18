# Dummy migration - already applied on Render
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('content', '0004_populate_user_interests'),
    ]
    operations = []

