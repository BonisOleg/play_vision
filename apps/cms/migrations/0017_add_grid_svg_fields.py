# Migration to add grid SVG fields to AboutSection3 and AboutSection4
# CRITICAL: AboutSection3/4 exist in DB but NOT in migration state after 0016
# Solution: Add models to state first, then add new fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0016_fix_experts_visibility'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                # STEP 1: Add AboutSection3 to migration state (with existing 9 fields from DB)
                migrations.CreateModel(
                    name='AboutSection3',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('title_ua', models.CharField(max_length=200, verbose_name='Заголовок (Україна)')),
                        ('title_world', models.CharField(blank=True, max_length=200, verbose_name='Заголовок (Світ)')),
                        ('svg_ua_light', models.TextField(verbose_name='SVG UA (світла тема)')),
                        ('svg_ua_dark', models.TextField(blank=True, verbose_name='SVG UA (темна тема)')),
                        ('svg_world_light', models.TextField(blank=True, verbose_name='SVG World (світла)')),
                        ('svg_world_dark', models.TextField(blank=True, verbose_name='SVG World (темна)')),
                        ('is_active', models.BooleanField(default=True, verbose_name='Активно')),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                    ],
                    options={
                        'verbose_name': 'Секція 3',
                        'verbose_name_plural': '📖 Про нас → Секція 3',
                        'db_table': 'cms_about_section3',
                    },
                ),
                # STEP 2: Add AboutSection4 to migration state (with existing 9 fields from DB)
                migrations.CreateModel(
                    name='AboutSection4',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('title_ua', models.CharField(max_length=200, verbose_name='Заголовок (Україна)')),
                        ('title_world', models.CharField(blank=True, max_length=200, verbose_name='Заголовок (Світ)')),
                        ('svg_ua_light', models.TextField(verbose_name='SVG UA (світла тема)')),
                        ('svg_ua_dark', models.TextField(blank=True, verbose_name='SVG UA (темна тема)')),
                        ('svg_world_light', models.TextField(blank=True, verbose_name='SVG World (світла)')),
                        ('svg_world_dark', models.TextField(blank=True, verbose_name='SVG World (темна)')),
                        ('is_active', models.BooleanField(default=True, verbose_name='Активно')),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                    ],
                    options={
                        'verbose_name': 'Секція 4',
                        'verbose_name_plural': '📖 Про нас → Секція 4',
                        'db_table': 'cms_about_section4',
                    },
                ),
                # STEP 3: Add new SVG fields to AboutSection3 in state
                migrations.AddField(
                    model_name='aboutsection3',
                    name='svg_1_ua_light',
                    field=models.TextField(blank=True, verbose_name='SVG 1 - UA (світла)'),
                ),
                migrations.AddField(
                    model_name='aboutsection3',
                    name='svg_1_ua_dark',
                    field=models.TextField(blank=True, verbose_name='SVG 1 - UA (темна)'),
                ),
                migrations.AddField(
                    model_name='aboutsection3',
                    name='svg_1_world_light',
                    field=models.TextField(blank=True, verbose_name='SVG 1 - World (світла)'),
                ),
                migrations.AddField(
                    model_name='aboutsection3',
                    name='svg_1_world_dark',
                    field=models.TextField(blank=True, verbose_name='SVG 1 - World (темна)'),
                ),
                migrations.AddField(
                    model_name='aboutsection3',
                    name='svg_2_ua_light',
                    field=models.TextField(blank=True, verbose_name='SVG 2 - UA (світла)'),
                ),
                migrations.AddField(
                    model_name='aboutsection3',
                    name='svg_2_ua_dark',
                    field=models.TextField(blank=True, verbose_name='SVG 2 - UA (темна)'),
                ),
                migrations.AddField(
                    model_name='aboutsection3',
                    name='svg_2_world_light',
                    field=models.TextField(blank=True, verbose_name='SVG 2 - World (світла)'),
                ),
                migrations.AddField(
                    model_name='aboutsection3',
                    name='svg_2_world_dark',
                    field=models.TextField(blank=True, verbose_name='SVG 2 - World (темна)'),
                ),
                migrations.AddField(
                    model_name='aboutsection3',
                    name='svg_3_ua_light',
                    field=models.TextField(blank=True, verbose_name='SVG 3 - UA (світла)'),
                ),
                migrations.AddField(
                    model_name='aboutsection3',
                    name='svg_3_ua_dark',
                    field=models.TextField(blank=True, verbose_name='SVG 3 - UA (темна)'),
                ),
                migrations.AddField(
                    model_name='aboutsection3',
                    name='svg_3_world_light',
                    field=models.TextField(blank=True, verbose_name='SVG 3 - World (світла)'),
                ),
                migrations.AddField(
                    model_name='aboutsection3',
                    name='svg_3_world_dark',
                    field=models.TextField(blank=True, verbose_name='SVG 3 - World (темна)'),
                ),
                # STEP 4: Add new SVG fields to AboutSection4 in state
                migrations.AddField(
                    model_name='aboutsection4',
                    name='svg_1_ua_light',
                    field=models.TextField(blank=True, verbose_name='SVG 1 - UA (світла)'),
                ),
                migrations.AddField(
                    model_name='aboutsection4',
                    name='svg_1_ua_dark',
                    field=models.TextField(blank=True, verbose_name='SVG 1 - UA (темна)'),
                ),
                migrations.AddField(
                    model_name='aboutsection4',
                    name='svg_1_world_light',
                    field=models.TextField(blank=True, verbose_name='SVG 1 - World (світла)'),
                ),
                migrations.AddField(
                    model_name='aboutsection4',
                    name='svg_1_world_dark',
                    field=models.TextField(blank=True, verbose_name='SVG 1 - World (темна)'),
                ),
                migrations.AddField(
                    model_name='aboutsection4',
                    name='svg_2_ua_light',
                    field=models.TextField(blank=True, verbose_name='SVG 2 - UA (світла)'),
                ),
                migrations.AddField(
                    model_name='aboutsection4',
                    name='svg_2_ua_dark',
                    field=models.TextField(blank=True, verbose_name='SVG 2 - UA (темна)'),
                ),
                migrations.AddField(
                    model_name='aboutsection4',
                    name='svg_2_world_light',
                    field=models.TextField(blank=True, verbose_name='SVG 2 - World (світла)'),
                ),
                migrations.AddField(
                    model_name='aboutsection4',
                    name='svg_2_world_dark',
                    field=models.TextField(blank=True, verbose_name='SVG 2 - World (темна)'),
                ),
                migrations.AddField(
                    model_name='aboutsection4',
                    name='svg_3_ua_light',
                    field=models.TextField(blank=True, verbose_name='SVG 3 - UA (світла)'),
                ),
                migrations.AddField(
                    model_name='aboutsection4',
                    name='svg_3_ua_dark',
                    field=models.TextField(blank=True, verbose_name='SVG 3 - UA (темна)'),
                ),
                migrations.AddField(
                    model_name='aboutsection4',
                    name='svg_3_world_light',
                    field=models.TextField(blank=True, verbose_name='SVG 3 - World (світла)'),
                ),
                migrations.AddField(
                    model_name='aboutsection4',
                    name='svg_3_world_dark',
                    field=models.TextField(blank=True, verbose_name='SVG 3 - World (темна)'),
                ),
                migrations.AddField(
                    model_name='aboutsection4',
                    name='svg_4_ua_light',
                    field=models.TextField(blank=True, verbose_name='SVG 4 - UA (світла)'),
                ),
                migrations.AddField(
                    model_name='aboutsection4',
                    name='svg_4_ua_dark',
                    field=models.TextField(blank=True, verbose_name='SVG 4 - UA (темна)'),
                ),
                migrations.AddField(
                    model_name='aboutsection4',
                    name='svg_4_world_light',
                    field=models.TextField(blank=True, verbose_name='SVG 4 - World (світла)'),
                ),
                migrations.AddField(
                    model_name='aboutsection4',
                    name='svg_4_world_dark',
                    field=models.TextField(blank=True, verbose_name='SVG 4 - World (темна)'),
                ),
                migrations.AddField(
                    model_name='aboutsection4',
                    name='svg_5_ua_light',
                    field=models.TextField(blank=True, verbose_name='SVG 5 - UA (світла)'),
                ),
                migrations.AddField(
                    model_name='aboutsection4',
                    name='svg_5_ua_dark',
                    field=models.TextField(blank=True, verbose_name='SVG 5 - UA (темна)'),
                ),
                migrations.AddField(
                    model_name='aboutsection4',
                    name='svg_5_world_light',
                    field=models.TextField(blank=True, verbose_name='SVG 5 - World (світла)'),
                ),
                migrations.AddField(
                    model_name='aboutsection4',
                    name='svg_5_world_dark',
                    field=models.TextField(blank=True, verbose_name='SVG 5 - World (темна)'),
                ),
                migrations.AddField(
                    model_name='aboutsection4',
                    name='svg_6_ua_light',
                    field=models.TextField(blank=True, verbose_name='SVG 6 - UA (світла)'),
                ),
                migrations.AddField(
                    model_name='aboutsection4',
                    name='svg_6_ua_dark',
                    field=models.TextField(blank=True, verbose_name='SVG 6 - UA (темна)'),
                ),
                migrations.AddField(
                    model_name='aboutsection4',
                    name='svg_6_world_light',
                    field=models.TextField(blank=True, verbose_name='SVG 6 - World (світла)'),
                ),
                migrations.AddField(
                    model_name='aboutsection4',
                    name='svg_6_world_dark',
                    field=models.TextField(blank=True, verbose_name='SVG 6 - World (темна)'),
                ),
            ],
            database_operations=[
                # Only add NEW fields to existing tables in DB
                # Tables cms_about_section3 and cms_about_section4 already exist!
                # AboutSection3 - Add 12 new SVG fields to DB
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section3 ADD COLUMN IF NOT EXISTS svg_1_ua_light TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section3 DROP COLUMN IF EXISTS svg_1_ua_light;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section3 ADD COLUMN IF NOT EXISTS svg_1_ua_dark TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section3 DROP COLUMN IF EXISTS svg_1_ua_dark;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section3 ADD COLUMN IF NOT EXISTS svg_1_world_light TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section3 DROP COLUMN IF EXISTS svg_1_world_light;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section3 ADD COLUMN IF NOT EXISTS svg_1_world_dark TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section3 DROP COLUMN IF EXISTS svg_1_world_dark;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section3 ADD COLUMN IF NOT EXISTS svg_2_ua_light TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section3 DROP COLUMN IF EXISTS svg_2_ua_light;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section3 ADD COLUMN IF NOT EXISTS svg_2_ua_dark TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section3 DROP COLUMN IF EXISTS svg_2_ua_dark;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section3 ADD COLUMN IF NOT EXISTS svg_2_world_light TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section3 DROP COLUMN IF EXISTS svg_2_world_light;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section3 ADD COLUMN IF NOT EXISTS svg_2_world_dark TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section3 DROP COLUMN IF EXISTS svg_2_world_dark;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section3 ADD COLUMN IF NOT EXISTS svg_3_ua_light TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section3 DROP COLUMN IF EXISTS svg_3_ua_light;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section3 ADD COLUMN IF NOT EXISTS svg_3_ua_dark TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section3 DROP COLUMN IF EXISTS svg_3_ua_dark;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section3 ADD COLUMN IF NOT EXISTS svg_3_world_light TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section3 DROP COLUMN IF EXISTS svg_3_world_light;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section3 ADD COLUMN IF NOT EXISTS svg_3_world_dark TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section3 DROP COLUMN IF EXISTS svg_3_world_dark;",
                ),
                # AboutSection4 - Add 24 new SVG fields to DB
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section4 ADD COLUMN IF NOT EXISTS svg_1_ua_light TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section4 DROP COLUMN IF EXISTS svg_1_ua_light;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section4 ADD COLUMN IF NOT EXISTS svg_1_ua_dark TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section4 DROP COLUMN IF EXISTS svg_1_ua_dark;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section4 ADD COLUMN IF NOT EXISTS svg_1_world_light TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section4 DROP COLUMN IF EXISTS svg_1_world_light;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section4 ADD COLUMN IF NOT EXISTS svg_1_world_dark TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section4 DROP COLUMN IF EXISTS svg_1_world_dark;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section4 ADD COLUMN IF NOT EXISTS svg_2_ua_light TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section4 DROP COLUMN IF EXISTS svg_2_ua_light;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section4 ADD COLUMN IF NOT EXISTS svg_2_ua_dark TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section4 DROP COLUMN IF EXISTS svg_2_ua_dark;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section4 ADD COLUMN IF NOT EXISTS svg_2_world_light TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section4 DROP COLUMN IF EXISTS svg_2_world_light;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section4 ADD COLUMN IF NOT EXISTS svg_2_world_dark TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section4 DROP COLUMN IF EXISTS svg_2_world_dark;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section4 ADD COLUMN IF NOT EXISTS svg_3_ua_light TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section4 DROP COLUMN IF EXISTS svg_3_ua_light;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section4 ADD COLUMN IF NOT EXISTS svg_3_ua_dark TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section4 DROP COLUMN IF EXISTS svg_3_ua_dark;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section4 ADD COLUMN IF NOT EXISTS svg_3_world_light TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section4 DROP COLUMN IF EXISTS svg_3_world_light;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section4 ADD COLUMN IF NOT EXISTS svg_3_world_dark TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section4 DROP COLUMN IF EXISTS svg_3_world_dark;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section4 ADD COLUMN IF NOT EXISTS svg_4_ua_light TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section4 DROP COLUMN IF EXISTS svg_4_ua_light;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section4 ADD COLUMN IF NOT EXISTS svg_4_ua_dark TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section4 DROP COLUMN IF EXISTS svg_4_ua_dark;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section4 ADD COLUMN IF NOT EXISTS svg_4_world_light TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section4 DROP COLUMN IF EXISTS svg_4_world_light;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section4 ADD COLUMN IF NOT EXISTS svg_4_world_dark TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section4 DROP COLUMN IF EXISTS svg_4_world_dark;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section4 ADD COLUMN IF NOT EXISTS svg_5_ua_light TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section4 DROP COLUMN IF EXISTS svg_5_ua_light;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section4 ADD COLUMN IF NOT EXISTS svg_5_ua_dark TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section4 DROP COLUMN IF EXISTS svg_5_ua_dark;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section4 ADD COLUMN IF NOT EXISTS svg_5_world_light TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section4 DROP COLUMN IF EXISTS svg_5_world_light;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section4 ADD COLUMN IF NOT EXISTS svg_5_world_dark TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section4 DROP COLUMN IF EXISTS svg_5_world_dark;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section4 ADD COLUMN IF NOT EXISTS svg_6_ua_light TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section4 DROP COLUMN IF EXISTS svg_6_ua_light;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section4 ADD COLUMN IF NOT EXISTS svg_6_ua_dark TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section4 DROP COLUMN IF EXISTS svg_6_ua_dark;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section4 ADD COLUMN IF NOT EXISTS svg_6_world_light TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section4 DROP COLUMN IF EXISTS svg_6_world_light;",
                ),
                migrations.RunSQL(
                    sql="ALTER TABLE cms_about_section4 ADD COLUMN IF NOT EXISTS svg_6_world_dark TEXT DEFAULT '';",
                    reverse_sql="ALTER TABLE cms_about_section4 DROP COLUMN IF EXISTS svg_6_world_dark;",
                ),
            ],
        ),
    ]
