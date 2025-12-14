# Generated migration for course badges and discounts

from django.db import migrations, models


def check_and_add_fields(apps, schema_editor):
    """Перевіряє існування колонок перед додаванням"""
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='courses' AND column_name IN ('has_discount', 'discount_percent', 'is_top_seller')
        """)
        existing_columns = {row[0] for row in cursor.fetchall()}
    
    db_table = 'courses'
    
    with schema_editor.connection.cursor() as cursor:
        if 'has_discount' not in existing_columns:
            cursor.execute(f"""
                ALTER TABLE {db_table} 
                ADD COLUMN has_discount BOOLEAN DEFAULT FALSE NOT NULL
            """)
            cursor.execute(f"CREATE INDEX IF NOT EXISTS courses_has_discount_idx ON {db_table}(has_discount)")
        
        if 'discount_percent' not in existing_columns:
            cursor.execute(f"""
                ALTER TABLE {db_table} 
                ADD COLUMN discount_percent INTEGER DEFAULT 0 NOT NULL
            """)
        
        if 'is_top_seller' not in existing_columns:
            cursor.execute(f"""
                ALTER TABLE {db_table} 
                ADD COLUMN is_top_seller BOOLEAN DEFAULT FALSE NOT NULL
            """)
            cursor.execute(f"CREATE INDEX IF NOT EXISTS courses_is_top_seller_idx ON {db_table}(is_top_seller)")


def reverse_migration(apps, schema_editor):
    """Відкат міграції"""
    db_table = 'courses'
    
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(f"DROP INDEX IF EXISTS courses_has_discount_idx")
        cursor.execute(f"DROP INDEX IF EXISTS courses_is_top_seller_idx")
        cursor.execute(f"ALTER TABLE {db_table} DROP COLUMN IF EXISTS has_discount")
        cursor.execute(f"ALTER TABLE {db_table} DROP COLUMN IF EXISTS discount_percent")
        cursor.execute(f"ALTER TABLE {db_table} DROP COLUMN IF EXISTS is_top_seller")


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0014_add_promo_video_fields'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(check_and_add_fields, reverse_migration),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='course',
                    name='has_discount',
                    field=models.BooleanField(default=False, db_index=True, help_text='Активувати знижку для цього курсу', verbose_name='Знижка активна'),
                ),
                migrations.AddField(
                    model_name='course',
                    name='discount_percent',
                    field=models.PositiveIntegerField(default=0, help_text='Вкажіть відсоток знижки (1-99%)', verbose_name='Відсоток знижки'),
                ),
                migrations.AddField(
                    model_name='course',
                    name='is_top_seller',
                    field=models.BooleanField(default=False, db_index=True, help_text='Показати бейдж "Топ продажів"', verbose_name='Топ продажів'),
                ),
            ],
        ),
    ]
