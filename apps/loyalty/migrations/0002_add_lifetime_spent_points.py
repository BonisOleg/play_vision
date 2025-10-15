# Generated migration to add missing column to existing table

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loyalty', '0001_initial'),
    ]

    operations = [
        # Спочатку перевіряємо і додаємо колонку якщо її немає
        migrations.RunSQL(
            sql="""
            DO $$
            BEGIN
                -- Перевірка існування таблиці loyalty_accounts
                IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'loyalty_accounts') THEN
                    -- Додати колонку lifetime_spent_points якщо її немає
                    IF NOT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = 'loyalty_accounts' 
                        AND column_name = 'lifetime_spent_points'
                    ) THEN
                        ALTER TABLE loyalty_accounts 
                        ADD COLUMN lifetime_spent_points INTEGER DEFAULT 0 NOT NULL;
                        
                        RAISE NOTICE 'Column lifetime_spent_points added successfully';
                    ELSE
                        RAISE NOTICE 'Column lifetime_spent_points already exists';
                    END IF;
                    
                    -- Перевірити чи існує колонка lifetime_spent (стара назва)
                    IF EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = 'loyalty_accounts' 
                        AND column_name = 'lifetime_spent'
                    ) THEN
                        -- Скопіювати дані зі старої колонки
                        UPDATE loyalty_accounts 
                        SET lifetime_spent_points = lifetime_spent 
                        WHERE lifetime_spent_points = 0 AND lifetime_spent > 0;
                        
                        -- Видалити стару колонку
                        ALTER TABLE loyalty_accounts DROP COLUMN lifetime_spent;
                        
                        RAISE NOTICE 'Migrated data from lifetime_spent to lifetime_spent_points';
                    END IF;
                    
                    -- Додати колонку lifetime_purchases якщо її немає
                    IF NOT EXISTS (
                        SELECT FROM information_schema.columns 
                        WHERE table_name = 'loyalty_accounts' 
                        AND column_name = 'lifetime_purchases'
                    ) THEN
                        ALTER TABLE loyalty_accounts 
                        ADD COLUMN lifetime_purchases NUMERIC(10, 2) DEFAULT 0 NOT NULL;
                        
                        RAISE NOTICE 'Column lifetime_purchases added successfully';
                    END IF;
                END IF;
                
                -- Створити таблицю point_earning_rules якщо її немає
                IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'point_earning_rules') THEN
                    CREATE TABLE point_earning_rules (
                        id BIGSERIAL PRIMARY KEY,
                        rule_type VARCHAR(20) NOT NULL,
                        subscription_tier VARCHAR(20) DEFAULT 'none' NOT NULL,
                        min_amount NUMERIC(10, 2),
                        max_amount NUMERIC(10, 2),
                        subscription_duration_months INTEGER,
                        points INTEGER NOT NULL,
                        is_active BOOLEAN DEFAULT TRUE NOT NULL,
                        "order" INTEGER DEFAULT 0 NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
                    );
                    CREATE INDEX point_earning_rules_order_idx ON point_earning_rules ("order", min_amount);
                    
                    RAISE NOTICE 'Table point_earning_rules created successfully';
                END IF;
                
                -- Створити таблицю point_transactions якщо її немає
                IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'point_transactions') THEN
                    CREATE TABLE point_transactions (
                        id BIGSERIAL PRIMARY KEY,
                        account_id BIGINT NOT NULL REFERENCES loyalty_accounts(id) ON DELETE CASCADE,
                        points INTEGER NOT NULL,
                        transaction_type VARCHAR(50) NOT NULL,
                        reason VARCHAR(255) NOT NULL,
                        reference_type VARCHAR(50) DEFAULT '',
                        reference_id INTEGER,
                        balance_after INTEGER NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
                    );
                    CREATE INDEX point_transactions_account_created_idx ON point_transactions (account_id, created_at DESC);
                    CREATE INDEX point_transactions_reference_idx ON point_transactions (reference_type, reference_id);
                    
                    RAISE NOTICE 'Table point_transactions created successfully';
                END IF;
                
                -- Створити таблицю redemption_options якщо її немає
                IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'redemption_options') THEN
                    CREATE TABLE redemption_options (
                        id BIGSERIAL PRIMARY KEY,
                        option_type VARCHAR(30) NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        description TEXT DEFAULT '',
                        points_required INTEGER NOT NULL,
                        discount_percentage INTEGER,
                        subscription_tier VARCHAR(20) DEFAULT '',
                        requires_subscription BOOLEAN DEFAULT FALSE NOT NULL,
                        is_active BOOLEAN DEFAULT TRUE NOT NULL,
                        display_order INTEGER DEFAULT 0 NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
                    );
                    CREATE INDEX redemption_options_display_idx ON redemption_options (display_order, points_required);
                    
                    RAISE NOTICE 'Table redemption_options created successfully';
                END IF;
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]

