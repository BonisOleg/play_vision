# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_event_event_category'),
    ]

    operations = [
        # Rename name to first_name
        migrations.RenameField(
            model_name='speaker',
            old_name='name',
            new_name='first_name',
        ),
        # Add last_name field
        migrations.AddField(
            model_name='speaker',
            name='last_name',
            field=models.CharField(max_length=50, default=''),
            preserve_default=False,
        ),
        # Add email uniqueness
        migrations.AddField(
            model_name='speaker',
            name='email',
            field=models.EmailField(max_length=254, unique=True, default=''),
            preserve_default=False,
        ),
        # Add is_active field
        migrations.AddField(
            model_name='speaker',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        # Add updated_at field
        migrations.AddField(
            model_name='speaker',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        # Add social links as separate fields
        migrations.AddField(
            model_name='speaker',
            name='linkedin_url',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='speaker',
            name='twitter_url',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='speaker',
            name='website_url',
            field=models.URLField(blank=True),
        ),
        # Remove social_links JSON field
        migrations.RemoveField(
            model_name='speaker',
            name='social_links',
        ),
        # Update ordering
        migrations.AlterModelOptions(
            name='speaker',
            options={
                'verbose_name': 'Speaker',
                'verbose_name_plural': 'Speakers',
                'db_table': 'speakers',
                'ordering': ['last_name', 'first_name'],
            },
        ),
    ]

