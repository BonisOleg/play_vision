# Add period-specific features and discount timers
# Safe migration with IF NOT EXISTS checks for Render compatibility
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0018_add_features_6_to_30'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DO $$ 
            BEGIN
                -- Add feature_1_monthly to feature_30_monthly
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_1_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_1_monthly VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_2_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_2_monthly VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_3_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_3_monthly VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_4_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_4_monthly VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_5_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_5_monthly VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_6_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_6_monthly VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_7_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_7_monthly VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_8_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_8_monthly VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_9_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_9_monthly VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_10_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_10_monthly VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_11_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_11_monthly VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_12_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_12_monthly VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_13_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_13_monthly VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_14_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_14_monthly VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_15_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_15_monthly VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_16_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_16_monthly VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_17_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_17_monthly VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_18_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_18_monthly VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_19_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_19_monthly VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_20_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_20_monthly VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_21_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_21_monthly VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_22_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_22_monthly VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_23_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_23_monthly VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_24_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_24_monthly VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_25_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_25_monthly VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_26_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_26_monthly VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_27_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_27_monthly VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_28_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_28_monthly VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_29_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_29_monthly VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_30_monthly'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_30_monthly VARCHAR(200) DEFAULT '';
                END IF;
                
                -- Add feature_1_3months to feature_30_3months
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_1_3months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_1_3months VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_2_3months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_2_3months VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_3_3months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_3_3months VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_4_3months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_4_3months VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_5_3months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_5_3months VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_6_3months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_6_3months VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_7_3months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_7_3months VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_8_3months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_8_3months VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_9_3months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_9_3months VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_10_3months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_10_3months VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_11_3months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_11_3months VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_12_3months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_12_3months VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_13_3months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_13_3months VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_14_3months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_14_3months VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_15_3months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_15_3months VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_16_3months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_16_3months VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_17_3months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_17_3months VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_18_3months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_18_3months VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_19_3months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_19_3months VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_20_3months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_20_3months VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_21_3months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_21_3months VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_22_3months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_22_3months VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_23_3months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_23_3months VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_24_3months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_24_3months VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_25_3months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_25_3months VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_26_3months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_26_3months VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_27_3months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_27_3months VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_28_3months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_28_3months VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_29_3months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_29_3months VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_30_3months'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_30_3months VARCHAR(200) DEFAULT '';
                END IF;
                
                -- Add discount timer fields
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='discount_monthly_percentage'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN discount_monthly_percentage INTEGER DEFAULT 0;
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='discount_monthly_start_date'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN discount_monthly_start_date TIMESTAMP WITH TIME ZONE NULL;
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='discount_monthly_end_date'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN discount_monthly_end_date TIMESTAMP WITH TIME ZONE NULL;
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='discount_3months_percentage'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN discount_3months_percentage INTEGER DEFAULT 0;
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='discount_3months_start_date'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN discount_3months_start_date TIMESTAMP WITH TIME ZONE NULL;
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='discount_3months_end_date'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN discount_3months_end_date TIMESTAMP WITH TIME ZONE NULL;
                END IF;
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
