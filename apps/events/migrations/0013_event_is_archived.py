# Generated migration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0012_event_is_online_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='is_archived',
            field=models.BooleanField(
                default=False,
                help_text='Відмітьте якщо подія вже відбулася. Дата/час необов\'язкові для архівних подій',
                verbose_name='Архівний івент',
            ),
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(
                fields=['is_archived', 'status'],
                name='events_is_archived_status_idx',
            ),
        ),
    ]

