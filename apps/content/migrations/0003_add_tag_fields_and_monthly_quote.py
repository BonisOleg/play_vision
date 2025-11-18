# Dummy migration - already applied on Render
from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('content', '0002_material_s3_video_key_material_secure_video_enabled_and_more'),
    ]
    operations = []

