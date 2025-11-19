# Verify and fix subscriptions table structure
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0004_remove_duration_months'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            DO $$ 
            BEGIN
                -- Таблиця subscriptions вже існує, просто перевіряємо структуру
                IF EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name='subscriptions'
                ) THEN
                    RAISE NOTICE 'Table subscriptions exists - verifying structure';
                    
                    -- Додаємо відсутні колонки якщо потрібно
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='subscriptions' AND column_name='start_date'
                    ) THEN
                        ALTER TABLE subscriptions ADD COLUMN start_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW();
                    END IF;
                    
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='subscriptions' AND column_name='end_date'
                    ) THEN
                        ALTER TABLE subscriptions ADD COLUMN end_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW();
                    END IF;
                    
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='subscriptions' AND column_name='auto_renew'
                    ) THEN
                        ALTER TABLE subscriptions ADD COLUMN auto_renew BOOLEAN NOT NULL DEFAULT FALSE;
                    END IF;
                    
                    -- Перевіряємо індекси
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_indexes 
                        WHERE tablename='subscriptions' AND indexname='subscriptions_user_id_idx'
                    ) THEN
                        CREATE INDEX subscriptions_user_id_idx ON subscriptions(user_id);
                    END IF;
                    
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_indexes 
                        WHERE tablename='subscriptions' AND indexname='subscriptions_plan_id_idx'
                    ) THEN
                        CREATE INDEX subscriptions_plan_id_idx ON subscriptions(plan_id);
                    END IF;
                    
                END IF;
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]

