# Generated migration for coming soon and new badges

from django.db import migrations, models


def check_and_add_fields(apps, schema_editor):
    """Перевіряє існування колонок перед додаванням"""
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='courses' AND column_name IN ('is_coming_soon', 'is_new')
        """)
        existing_columns = {row[0] for row in cursor.fetchall()}
    
    db_table = 'courses'
    
    with schema_editor.connection.cursor() as cursor:
        if 'is_coming_soon' not in existing_columns:
            cursor.execute(f"""
                ALTER TABLE {db_table} 
                ADD COLUMN is_coming_soon BOOLEAN DEFAULT FALSE NOT NULL
            """)
            cursor.execute(f"CREATE INDEX IF NOT EXISTS courses_is_coming_soon_idx ON {db_table}(is_coming_soon)")
        
        if 'is_new' not in existing_columns:
            cursor.execute(f"""
                ALTER TABLE {db_table} 
                ADD COLUMN is_new BOOLEAN DEFAULT FALSE NOT NULL
            """)
            cursor.execute(f"CREATE INDEX IF NOT EXISTS courses_is_new_idx ON {db_table}(is_new)")


def reverse_migration(apps, schema_editor):
    """Відкат міграції"""
    db_table = 'courses'
    
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(f"DROP INDEX IF EXISTS courses_is_coming_soon_idx")
        cursor.execute(f"DROP INDEX IF EXISTS courses_is_new_idx")
        cursor.execute(f"ALTER TABLE {db_table} DROP COLUMN IF EXISTS is_coming_soon")
        cursor.execute(f"ALTER TABLE {db_table} DROP COLUMN IF EXISTS is_new")


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0016_add_subscription_text'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(check_and_add_fields, reverse_migration),
            ],
            state_operations=[
                migrations.AddField(
                    model_name='course',
                    name='is_coming_soon',
                    field=models.BooleanField(default=False, db_index=True, help_text='Показати бейдж "Незабаром"', verbose_name='Незабаром'),
                ),
                migrations.AddField(
                    model_name='course',
                    name='is_new',
                    field=models.BooleanField(default=False, db_index=True, help_text='Показати бейдж "Новинка"', verbose_name='Новинка'),
                ),
            ],
        ),
    ]
