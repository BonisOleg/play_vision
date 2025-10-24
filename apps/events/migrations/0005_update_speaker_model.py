# Generated manually - idempotent migration for Speaker model updates

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_event_event_category'),
    ]

    operations = [
        # Rename name to first_name if name exists and first_name doesn't
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='speakers' AND column_name='name'
                    ) AND NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='speakers' AND column_name='first_name'
                    ) THEN
                        ALTER TABLE speakers RENAME COLUMN name TO first_name;
                    END IF;
                END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        
        # Add last_name if it doesn't exist
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='speakers' AND column_name='last_name'
                    ) THEN
                        ALTER TABLE speakers ADD COLUMN last_name VARCHAR(50) DEFAULT '' NOT NULL;
                    END IF;
                END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        
        # Add email if it doesn't exist
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='speakers' AND column_name='email'
                    ) THEN
                        ALTER TABLE speakers ADD COLUMN email VARCHAR(254) DEFAULT '' NOT NULL;
                    END IF;
                END $$;
                
                -- Add unique constraint if it doesn't exist
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM pg_constraint 
                        WHERE conname = 'speakers_email_unique'
                    ) THEN
                        ALTER TABLE speakers ADD CONSTRAINT speakers_email_unique UNIQUE (email);
                    END IF;
                EXCEPTION
                    WHEN others THEN
                        -- If constraint creation fails, just continue
                        NULL;
                END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        
        # Add is_active if it doesn't exist
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='speakers' AND column_name='is_active'
                    ) THEN
                        ALTER TABLE speakers ADD COLUMN is_active BOOLEAN DEFAULT TRUE NOT NULL;
                    END IF;
                END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        
        # Add updated_at if it doesn't exist
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='speakers' AND column_name='updated_at'
                    ) THEN
                        ALTER TABLE speakers ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL;
                    END IF;
                END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        
        # Add social media fields if they don't exist
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='speakers' AND column_name='linkedin_url'
                    ) THEN
                        ALTER TABLE speakers ADD COLUMN linkedin_url VARCHAR(200) DEFAULT '' NOT NULL;
                    END IF;
                    
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='speakers' AND column_name='twitter_url'
                    ) THEN
                        ALTER TABLE speakers ADD COLUMN twitter_url VARCHAR(200) DEFAULT '' NOT NULL;
                    END IF;
                    
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='speakers' AND column_name='website_url'
                    ) THEN
                        ALTER TABLE speakers ADD COLUMN website_url VARCHAR(200) DEFAULT '' NOT NULL;
                    END IF;
                END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
        
        # Remove social_links column if it exists
        migrations.RunSQL(
            sql="""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name='speakers' AND column_name='social_links'
                    ) THEN
                        ALTER TABLE speakers DROP COLUMN social_links;
                    END IF;
                END $$;
            """,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]

