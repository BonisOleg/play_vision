# Dummy migration - already applied on Render
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('content', '0003_add_tag_fields_and_monthly_quote'),
    ]
    operations = []

