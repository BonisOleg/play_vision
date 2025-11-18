# Dummy migration - already applied on Render
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('content', '0007_add_bunny_net_fields'),
    ]
    operations = []

