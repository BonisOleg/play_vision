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
                -- Rename registration_data to custom_fields if it exists
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='event_registrations' AND column_name='registration_data'
                ) THEN
                    ALTER TABLE event_registrations RENAME COLUMN registration_data TO custom_fields;
                END IF;
            END $$;
            """,
            reverse_sql="""
            ALTER TABLE event_registrations RENAME COLUMN custom_fields TO registration_data;
            """,
        ),
    ]

