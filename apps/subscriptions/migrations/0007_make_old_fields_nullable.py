# Make old fields nullable for backward compatibility
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0006_cleanup_old_columns'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DO $$ 
            BEGIN
                -- Зробити старі поля nullable (дозволити NULL)
                -- Ці поля більше не використовуються в новій версії
                
                -- price -> nullable
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='price'
                ) THEN
                    ALTER TABLE subscription_plans ALTER COLUMN price DROP NOT NULL;
                    ALTER TABLE subscription_plans ALTER COLUMN price SET DEFAULT 0;
                    RAISE NOTICE 'Made price nullable';
                END IF;
                
                -- features -> nullable
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='features'
                ) THEN
                    ALTER TABLE subscription_plans ALTER COLUMN features DROP NOT NULL;
                    ALTER TABLE subscription_plans ALTER COLUMN features SET DEFAULT '[]'::jsonb;
                    RAISE NOTICE 'Made features nullable';
                END IF;
                
                -- event_tickets_balance -> nullable
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='event_tickets_balance'
                ) THEN
                    ALTER TABLE subscription_plans ALTER COLUMN event_tickets_balance DROP NOT NULL;
                    ALTER TABLE subscription_plans ALTER COLUMN event_tickets_balance SET DEFAULT 0;
                    RAISE NOTICE 'Made event_tickets_balance nullable';
                END IF;
                
                -- discount_percentage -> nullable
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='discount_percentage'
                ) THEN
                    ALTER TABLE subscription_plans ALTER COLUMN discount_percentage DROP NOT NULL;
                    ALTER TABLE subscription_plans ALTER COLUMN discount_percentage SET DEFAULT 0;
                    RAISE NOTICE 'Made discount_percentage nullable';
                END IF;
                
                -- is_best_value -> nullable
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='is_best_value'
                ) THEN
                    ALTER TABLE subscription_plans ALTER COLUMN is_best_value DROP NOT NULL;
                    ALTER TABLE subscription_plans ALTER COLUMN is_best_value SET DEFAULT FALSE;
                END IF;
                
                -- badge_type -> nullable
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='badge_type'
                ) THEN
                    ALTER TABLE subscription_plans ALTER COLUMN badge_type DROP NOT NULL;
                    ALTER TABLE subscription_plans ALTER COLUMN badge_type SET DEFAULT '';
                END IF;
                
                -- total_subscriptions -> nullable
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='subscription_plans' AND column_name='total_subscriptions'
                ) THEN
                    ALTER TABLE subscription_plans ALTER COLUMN total_subscriptions DROP NOT NULL;
                    ALTER TABLE subscription_plans ALTER COLUMN total_subscriptions SET DEFAULT 0;
                END IF;
                
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]

