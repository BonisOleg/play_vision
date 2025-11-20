# Generated manually to remove legacy category field from database
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0012_alter_course_logo_alter_course_preview_video_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                # Видалити foreign key constraint
                "ALTER TABLE courses DROP CONSTRAINT IF EXISTS courses_category_id_fkey CASCADE;",
                # Видалити поле category_id з таблиці courses
                "ALTER TABLE courses DROP COLUMN IF EXISTS category_id CASCADE;",
                # Видалити таблицю categories (якщо існує)
                "DROP TABLE IF EXISTS categories CASCADE;",
                # Видалити таблицю tags (якщо існує, оскільки більше не використовується)
                "DROP TABLE IF EXISTS tags CASCADE;",
                # Видалити зв'язкову таблицю course-tags (якщо існує)
                "DROP TABLE IF EXISTS content_course_tags CASCADE;",
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]

