# Refactor pricing logic: replace base_price + discount_percentage with original_price + sale_price
# Safe migration with IF EXISTS/IF NOT EXISTS checks for Render compatibility
from django.db import migrations
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0022_add_base_price_3months_fields'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DO $$ 
            BEGIN
                -- Add new pricing fields for monthly subscription
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='original_price_monthly_uah'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN original_price_monthly_uah DECIMAL(10,2) DEFAULT 0;
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='original_price_monthly_usd'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN original_price_monthly_usd DECIMAL(10,2) DEFAULT 0;
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='sale_price_monthly_uah'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN sale_price_monthly_uah DECIMAL(10,2) DEFAULT 0;
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='sale_price_monthly_usd'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN sale_price_monthly_usd DECIMAL(10,2) DEFAULT 0;
                END IF;
                
                -- Add new pricing fields for 3 months subscription
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='original_price_3months_uah'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN original_price_3months_uah DECIMAL(10,2) DEFAULT 0;
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='original_price_3months_usd'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN original_price_3months_usd DECIMAL(10,2) DEFAULT 0;
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='sale_price_3months_uah'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN sale_price_3months_uah DECIMAL(10,2) DEFAULT 0;
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='sale_price_3months_usd'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN sale_price_3months_usd DECIMAL(10,2) DEFAULT 0;
                END IF;
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Convert existing data from old fields to new fields
        migrations.RunSQL(
            sql="""
            DO $$ 
            DECLARE
                rec RECORD;
                base_monthly_uah DECIMAL(10,2);
                base_monthly_usd DECIMAL(10,2);
                base_3m_uah DECIMAL(10,2);
                base_3m_usd DECIMAL(10,2);
                discount_monthly_pct INTEGER;
                discount_3m_pct INTEGER;
                calculated_sale_monthly_uah DECIMAL(10,2);
                calculated_sale_monthly_usd DECIMAL(10,2);
                calculated_sale_3m_uah DECIMAL(10,2);
                calculated_sale_3m_usd DECIMAL(10,2);
            BEGIN
                FOR rec IN SELECT id FROM subscription_plans LOOP
                    -- Get old values (with defaults if NULL)
                    SELECT COALESCE(base_price_uah, 0) INTO base_monthly_uah FROM subscription_plans WHERE id = rec.id;
                    SELECT COALESCE(base_price_usd, 0) INTO base_monthly_usd FROM subscription_plans WHERE id = rec.id;
                    SELECT COALESCE(base_price_3months_uah, 0) INTO base_3m_uah FROM subscription_plans WHERE id = rec.id;
                    SELECT COALESCE(base_price_3months_usd, 0) INTO base_3m_usd FROM subscription_plans WHERE id = rec.id;
                    SELECT COALESCE(discount_monthly, 0) INTO discount_monthly_pct FROM subscription_plans WHERE id = rec.id;
                    SELECT COALESCE(discount_3_months, 0) INTO discount_3m_pct FROM subscription_plans WHERE id = rec.id;
                    
                    -- If base_price_3months is 0, calculate from monthly * 3
                    IF base_3m_uah = 0 AND base_monthly_uah > 0 THEN
                        base_3m_uah := base_monthly_uah * 3;
                    END IF;
                    IF base_3m_usd = 0 AND base_monthly_usd > 0 THEN
                        base_3m_usd := base_monthly_usd * 3;
                    END IF;
                    
                    -- Calculate sale prices from old discount percentages
                    IF base_monthly_uah > 0 AND discount_monthly_pct > 0 THEN
                        calculated_sale_monthly_uah := base_monthly_uah * (1 - discount_monthly_pct / 100.0);
                    ELSE
                        calculated_sale_monthly_uah := base_monthly_uah;
                    END IF;
                    
                    IF base_monthly_usd > 0 AND discount_monthly_pct > 0 THEN
                        calculated_sale_monthly_usd := base_monthly_usd * (1 - discount_monthly_pct / 100.0);
                    ELSE
                        calculated_sale_monthly_usd := base_monthly_usd;
                    END IF;
                    
                    IF base_3m_uah > 0 AND discount_3m_pct > 0 THEN
                        calculated_sale_3m_uah := base_3m_uah * (1 - discount_3m_pct / 100.0);
                    ELSE
                        calculated_sale_3m_uah := base_3m_uah;
                    END IF;
                    
                    IF base_3m_usd > 0 AND discount_3m_pct > 0 THEN
                        calculated_sale_3m_usd := base_3m_usd * (1 - discount_3m_pct / 100.0);
                    ELSE
                        calculated_sale_3m_usd := base_3m_usd;
                    END IF;
                    
                    -- Update new fields with converted data
                    -- original_price = base_price
                    UPDATE subscription_plans 
                    SET 
                        original_price_monthly_uah = base_monthly_uah,
                        original_price_monthly_usd = base_monthly_usd,
                        original_price_3months_uah = base_3m_uah,
                        original_price_3months_usd = base_3m_usd,
                        sale_price_monthly_uah = calculated_sale_monthly_uah,
                        sale_price_monthly_usd = calculated_sale_monthly_usd,
                        sale_price_3months_uah = calculated_sale_3m_uah,
                        sale_price_3months_usd = calculated_sale_3m_usd
                    WHERE id = rec.id;
                END LOOP;
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Make old fields nullable (they will be removed in a future migration if needed)
        migrations.RunSQL(
            sql="""
            DO $$ 
            BEGIN
                -- Make old fields nullable
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='base_price_uah' AND is_nullable='NO'
                ) THEN
                    ALTER TABLE subscription_plans ALTER COLUMN base_price_uah DROP NOT NULL;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='base_price_usd' AND is_nullable='NO'
                ) THEN
                    ALTER TABLE subscription_plans ALTER COLUMN base_price_usd DROP NOT NULL;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='base_price_3months_uah' AND is_nullable='NO'
                ) THEN
                    ALTER TABLE subscription_plans ALTER COLUMN base_price_3months_uah DROP NOT NULL;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='base_price_3months_usd' AND is_nullable='NO'
                ) THEN
                    ALTER TABLE subscription_plans ALTER COLUMN base_price_3months_usd DROP NOT NULL;
                END IF;
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]

