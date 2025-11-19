# Clean up all old fields that don't exist in current model
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0005_ensure_user_subscriptions_table'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DO $$ 
            DECLARE
                r RECORD;
                table_columns TEXT[];
                expected_columns TEXT[] := ARRAY[
                    'id', 'name', 'slug', 'badge_text', 'badge_color',
                    'feature_1', 'feature_2', 'feature_3', 'feature_4', 'feature_5',
                    'base_price_uah', 'base_price_usd',
                    'discount_3_months', 'discount_12_months',
                    'available_monthly', 'available_3_months', 'available_12_months',
                    'unavailable_text', 'checkout_url',
                    'display_order', 'is_active', 'is_popular',
                    'meta_title', 'meta_description',
                    'created_at', 'updated_at'
                ];
            BEGIN
                -- Remove any columns that are not in our expected list
                FOR r IN 
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'subscription_plans' 
                      AND column_name NOT IN (SELECT unnest(expected_columns))
                LOOP
                    RAISE NOTICE 'Dropping old column: %', r.column_name;
                    EXECUTE format('ALTER TABLE subscription_plans DROP COLUMN IF EXISTS %I', r.column_name);
                END LOOP;
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]

