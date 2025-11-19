# Fix field name for EventRegistration: registration_data -> custom_fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_eventticket_tier_name'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DO $$ 
            BEGIN
                -- Check if custom_fields already exists
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='event_registrations' AND column_name='custom_fields'
                ) THEN
                    -- custom_fields exists, so just remove registration_data if it exists
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='event_registrations' AND column_name='registration_data'
                    ) THEN
                        -- Copy data from registration_data to custom_fields if custom_fields is empty
                        UPDATE event_registrations 
                        SET custom_fields = registration_data 
                        WHERE (custom_fields IS NULL OR custom_fields::text = '{}') 
                          AND registration_data IS NOT NULL;
                        
                        -- Drop the old column
                        ALTER TABLE event_registrations DROP COLUMN registration_data;
                    END IF;
                ELSE
                    -- custom_fields doesn't exist, rename registration_data if it exists
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='event_registrations' AND column_name='registration_data'
                    ) THEN
                        ALTER TABLE event_registrations RENAME COLUMN registration_data TO custom_fields;
                    END IF;
                END IF;
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]

