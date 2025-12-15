# Add base_price_3months_uah and base_price_3months_usd fields
# Safe migration with IF NOT EXISTS checks for Render compatibility
# This migration ensures these fields exist even if 0021 was not applied
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0021_refactor_discounts'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DO $$ 
            BEGIN
                -- Add base_price_3months_uah if not exists
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='base_price_3months_uah'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN base_price_3months_uah DECIMAL(10,2) DEFAULT 0;
                END IF;
                
                -- Add base_price_3months_usd if not exists
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='base_price_3months_usd'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN base_price_3months_usd DECIMAL(10,2) DEFAULT 0;
                END IF;
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]

