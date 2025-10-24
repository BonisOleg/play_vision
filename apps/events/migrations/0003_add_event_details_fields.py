# Generated manually - idempotent migration

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_add_missing_fields'),
    ]

    operations = [
        # Add benefits field if it doesn't exist
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='events' AND column_name='benefits'
                    ) THEN
                        ALTER TABLE events ADD COLUMN benefits JSONB DEFAULT '[]'::jsonb NOT NULL;
                    END IF;
                END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        
        # Add target_audience field if it doesn't exist
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='events' AND column_name='target_audience'
                    ) THEN
                        ALTER TABLE events ADD COLUMN target_audience JSONB DEFAULT '[]'::jsonb NOT NULL;
                    END IF;
                END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        
        # Add ticket_tiers field if it doesn't exist
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='events' AND column_name='ticket_tiers'
                    ) THEN
                        ALTER TABLE events ADD COLUMN ticket_tiers JSONB DEFAULT '[]'::jsonb NOT NULL;
                    END IF;
                END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
