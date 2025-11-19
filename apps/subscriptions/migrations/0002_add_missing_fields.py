# Generated manually to add missing fields to existing table
from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0001_initial'),
    ]

    operations = [
        # Check if badge_color exists, if not add all missing fields
        migrations.RunSQL(
            sql="""
            DO $$ 
            BEGIN
                -- Add badge_color if not exists
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='badge_color'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN badge_color VARCHAR(7) DEFAULT '#3B82F6';
                END IF;
                
                -- Add all other potentially missing fields
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_1'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_1 VARCHAR(200) NOT NULL DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_2'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_2 VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_3'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_3 VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_4'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_4 VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_5'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_5 VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='base_price_uah'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN base_price_uah DECIMAL(10,2) NOT NULL DEFAULT 0;
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='base_price_usd'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN base_price_usd DECIMAL(10,2) NOT NULL DEFAULT 0;
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='discount_3_months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN discount_3_months INTEGER DEFAULT 0;
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='discount_12_months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN discount_12_months INTEGER DEFAULT 0;
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='available_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN available_monthly BOOLEAN DEFAULT TRUE;
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='available_3_months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN available_3_months BOOLEAN DEFAULT TRUE;
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='available_12_months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN available_12_months BOOLEAN DEFAULT TRUE;
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='unavailable_text'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN unavailable_text VARCHAR(100) DEFAULT 'Доступно в тарифі від 3 місяців';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='checkout_url'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN checkout_url VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='display_order'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN display_order INTEGER DEFAULT 0;
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='is_active'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN is_active BOOLEAN DEFAULT TRUE;
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='is_popular'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN is_popular BOOLEAN DEFAULT FALSE;
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='meta_title'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN meta_title VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='meta_description'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN meta_description TEXT DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='created_at'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN created_at TIMESTAMP DEFAULT NOW();
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='updated_at'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN updated_at TIMESTAMP DEFAULT NOW();
                END IF;
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
