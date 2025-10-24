# Generated manually - idempotent migration

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_add_event_details_fields'),
    ]

    operations = [
        # Add event_category field if it doesn't exist
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='events' AND column_name='event_category'
                    ) THEN
                        ALTER TABLE events ADD COLUMN event_category VARCHAR(50) DEFAULT '' NOT NULL;
                    END IF;
                END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]

