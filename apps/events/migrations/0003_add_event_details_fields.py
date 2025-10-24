# Generated manually - safe migration that only adds fields if they don't exist

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_add_missing_fields'),
    ]

    operations = [
        # This migration is safe - it only adds columns if they don't already exist
        migrations.RunSQL(
            sql="""
                -- Add benefits field if it doesn't exist
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='events' AND column_name='benefits'
                    ) THEN
                        ALTER TABLE events ADD COLUMN benefits JSONB DEFAULT '[]'::jsonb;
                    END IF;
                END $$;
                
                -- Add target_audience field if it doesn't exist
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='events' AND column_name='target_audience'
                    ) THEN
                        ALTER TABLE events ADD COLUMN target_audience JSONB DEFAULT '[]'::jsonb;
                    END IF;
                END $$;
                
                -- Add ticket_tiers field if it doesn't exist
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='events' AND column_name='ticket_tiers'
                    ) THEN
                        ALTER TABLE events ADD COLUMN ticket_tiers JSONB DEFAULT '[]'::jsonb;
                    END IF;
                END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
