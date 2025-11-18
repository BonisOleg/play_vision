# Dummy migration - already applied on Render
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('content', '0005_add_author_and_target_audience'),
    ]
    operations = []

