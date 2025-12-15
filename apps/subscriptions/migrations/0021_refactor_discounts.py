# Refactor discounts: add discount_monthly, remove discount_12_months and available_12_months
# Safe migration with IF EXISTS checks for Render compatibility
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0020_remove_old_feature_fields'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DO $$ 
            BEGIN
                -- Add discount_monthly if not exists
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='discount_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN discount_monthly INTEGER DEFAULT 0;
                END IF;
                
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
                
                -- Remove discount_12_months if exists
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='discount_12_months'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN discount_12_months;
                END IF;
                
                -- Remove available_12_months if exists
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='available_12_months'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN available_12_months;
                END IF;
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]

