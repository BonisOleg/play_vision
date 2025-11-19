# Remove old 'duration' field that doesn't exist in model
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0002_add_missing_fields'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DO $$ 
            BEGIN
                -- Remove duration column if it exists
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='duration'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN duration;
                END IF;
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
