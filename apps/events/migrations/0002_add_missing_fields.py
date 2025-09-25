# Generated manually to fix missing fields on production

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        # Add requires_subscription field if it doesn't exist
        migrations.RunSQL(
            sql="ALTER TABLE events ADD COLUMN IF NOT EXISTS requires_subscription BOOLEAN DEFAULT FALSE;",
            reverse_sql="ALTER TABLE events DROP COLUMN IF EXISTS requires_subscription;",
            state_operations=[
                migrations.AddField(
                    model_name='event',
                    name='requires_subscription',
                    field=models.BooleanField(default=False, help_text='Чи можна використати квитки з підписки'),
                ),
            ]
        ),
        
        # Update price field to add validator
        migrations.RunSQL(
            sql="ALTER TABLE events ALTER COLUMN price SET DEFAULT 0;",  # Ensure it has default
            reverse_sql="ALTER TABLE events ALTER COLUMN price SET DEFAULT 0;",
            state_operations=[
                migrations.AlterField(
                    model_name='event',
                    name='price',
                    field=models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)]),
                ),
            ]
        ),
        
        # Update is_free default value
        migrations.RunSQL(
            sql="ALTER TABLE events ALTER COLUMN is_free SET DEFAULT FALSE;",
            reverse_sql="ALTER TABLE events ALTER COLUMN is_free SET DEFAULT TRUE;",
            state_operations=[
                migrations.AlterField(
                    model_name='event',
                    name='is_free',
                    field=models.BooleanField(default=False),
                ),
            ]
        ),
        
        # Ensure organizer_id column exists (should be there but let's be safe)
        migrations.RunSQL(
            sql="""
            DO $$ 
            BEGIN 
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='events' AND column_name='organizer_id') 
                THEN
                    ALTER TABLE events ADD COLUMN organizer_id BIGINT;
                    ALTER TABLE events ADD CONSTRAINT events_organizer_id_fk FOREIGN KEY (organizer_id) REFERENCES users(id);
                END IF; 
            END $$;
            """,
            reverse_sql="ALTER TABLE events DROP COLUMN IF EXISTS organizer_id;",
            state_operations=[
                # This field should already exist from initial migration
                # but adding it here for completeness
            ]
        ),
    ]
