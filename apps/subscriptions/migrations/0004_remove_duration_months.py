# Remove old 'duration_months' field that doesn't exist in model
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0003_remove_duration_field'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DO $$ 
            BEGIN
                -- Remove duration_months column if it exists
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='duration_months'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN duration_months;
                END IF;
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]

