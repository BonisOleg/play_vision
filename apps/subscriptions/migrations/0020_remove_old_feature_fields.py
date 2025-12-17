# Remove old feature_1 to feature_30 fields
# Safe migration with IF EXISTS checks for Render compatibility
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0019_add_period_features_and_discount_timers'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DO $$ 
            BEGIN
                -- Remove feature_1 to feature_30 if they exist
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_1'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN feature_1;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_2'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN feature_2;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_3'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN feature_3;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_4'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN feature_4;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_5'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN feature_5;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_6'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN feature_6;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_7'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN feature_7;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_8'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN feature_8;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_9'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN feature_9;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_10'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN feature_10;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_11'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN feature_11;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_12'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN feature_12;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_13'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN feature_13;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_14'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN feature_14;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_15'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN feature_15;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_16'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN feature_16;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_17'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN feature_17;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_18'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN feature_18;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_19'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN feature_19;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_20'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN feature_20;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_21'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN feature_21;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_22'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN feature_22;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_23'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN feature_23;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_24'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN feature_24;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_25'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN feature_25;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_26'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN feature_26;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_27'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN feature_27;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_28'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN feature_28;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_29'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN feature_29;
                END IF;
                
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_30'
                ) THEN
                    ALTER TABLE subscription_plans DROP COLUMN feature_30;
                END IF;
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]

