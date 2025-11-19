# Ensure user_subscriptions table exists
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
                -- Create user_subscriptions table if it doesn't exist
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.tables 
                    WHERE table_name='user_subscriptions'
                ) THEN
                    CREATE TABLE user_subscriptions (
                        id BIGSERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        plan_id INTEGER NOT NULL,
                        start_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        end_date TIMESTAMP WITH TIME ZONE NOT NULL,
                        is_active BOOLEAN NOT NULL DEFAULT TRUE,
                        auto_renew BOOLEAN NOT NULL DEFAULT FALSE,
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        CONSTRAINT user_subscriptions_user_id_fkey 
                            FOREIGN KEY (user_id) REFERENCES accounts_user(id) ON DELETE CASCADE,
                        CONSTRAINT user_subscriptions_plan_id_fkey 
                            FOREIGN KEY (plan_id) REFERENCES subscription_plans(id) ON DELETE CASCADE
                    );
                    
                    -- Create indexes
                    CREATE INDEX user_subscriptions_user_id_idx ON user_subscriptions(user_id);
                    CREATE INDEX user_subscriptions_plan_id_idx ON user_subscriptions(plan_id);
                    CREATE INDEX user_subscriptions_created_at_idx ON user_subscriptions(created_at DESC);
                    CREATE INDEX user_subscriptions_is_active_idx ON user_subscriptions(is_active);
                END IF;
            END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]

