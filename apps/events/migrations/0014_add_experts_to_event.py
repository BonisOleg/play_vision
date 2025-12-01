# Generated migration for adding experts ManyToManyField to Event

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0013_event_is_archived'),
        ('cms', '0014_add_page_selection_expertcard'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='experts',
            field=models.ManyToManyField(
                blank=True,
                help_text='Члени команди Play Vision як спікери',
                related_name='expert_events',
                to='cms.expertcard',
                verbose_name='Експерти команди',
            ),
        ),
    ]

