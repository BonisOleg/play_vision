from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('landing', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='leadsubmission',
            old_name='full_name',
            new_name='first_name',
        ),
    ]

