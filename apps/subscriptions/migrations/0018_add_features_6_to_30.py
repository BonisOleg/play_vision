# Add features 6-30 to subscription plans
# Safe migration with IF NOT EXISTS checks for Render compatibility
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0007_make_old_fields_nullable'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DO $$ 
            BEGIN
                -- Add feature_6 to feature_30 if they don't exist
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_6'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_6 VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_7'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_7 VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_8'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_8 VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_9'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_9 VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_10'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_10 VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_11'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_11 VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_12'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_12 VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_13'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_13 VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_14'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_14 VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_15'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_15 VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_16'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_16 VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_17'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_17 VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_18'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_18 VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_19'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_19 VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_20'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_20 VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_21'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_21 VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_22'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_22 VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_23'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_23 VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_24'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_24 VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_25'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_25 VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_26'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_26 VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_27'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_27 VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_28'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_28 VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_29'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_29 VARCHAR(200) DEFAULT '';
                END IF;
                
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='feature_30'
                ) THEN
                    ALTER TABLE subscription_plans ADD COLUMN feature_30 VARCHAR(200) DEFAULT '';
                END IF;
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
