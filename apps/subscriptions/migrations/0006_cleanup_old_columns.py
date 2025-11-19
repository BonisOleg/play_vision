# Clean up old columns that don't exist in current model
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0005_verify_subscriptions_table'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DO $$ 
            DECLARE
                expected_columns TEXT[] := ARRAY[
                    'id', 'name', 'slug', 'badge_text', 'badge_color',
                    'feature_1', 'feature_2', 'feature_3', 'feature_4', 'feature_5',
                    'base_price_uah', 'base_price_usd',
                    'discount_3_months', 'discount_12_months',
                    'available_monthly', 'available_3_months', 'available_12_months',
                    'unavailable_text', 'checkout_url',
                    'display_order', 'is_active', 'is_popular',
                    'meta_title', 'meta_description',
                    'created_at', 'updated_at',
                    -- Старі поля які залишаємо для сумісності
                    'price', 'features', 'event_tickets_balance', 
                    'discount_percentage', 'is_best_value', 'badge_type', 'total_subscriptions'
                ];
                r RECORD;
            BEGIN
                -- Видаляємо тільки duration_months якщо він є
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'subscription_plans' AND column_name = 'duration_months'
                ) THEN
                    RAISE NOTICE 'Dropping old column: duration_months';
                    ALTER TABLE subscription_plans DROP COLUMN duration_months;
                END IF;
                
                -- Видаляємо duration якщо він є
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'subscription_plans' AND column_name = 'duration'
                ) THEN
                    RAISE NOTICE 'Dropping old column: duration';
                    ALTER TABLE subscription_plans DROP COLUMN duration;
                END IF;
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]

