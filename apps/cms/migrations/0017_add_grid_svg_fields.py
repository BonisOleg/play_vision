# Migration to add grid SVG fields to AboutSection3 and AboutSection4
# Uses SeparateDatabaseAndState because models from 0007 are not fully in state

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0016_fix_experts_visibility'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                # Add model definitions to state (from 0007 they were only in database)
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
                        ('svg_1_ua_light', models.TextField(blank=True, verbose_name='SVG 1 - UA (світла)')),
                        ('svg_1_ua_dark', models.TextField(blank=True, verbose_name='SVG 1 - UA (темна)')),
                        ('svg_1_world_light', models.TextField(blank=True, verbose_name='SVG 1 - World (світла)')),
                        ('svg_1_world_dark', models.TextField(blank=True, verbose_name='SVG 1 - World (темна)')),
                        ('svg_2_ua_light', models.TextField(blank=True, verbose_name='SVG 2 - UA (світла)')),
                        ('svg_2_ua_dark', models.TextField(blank=True, verbose_name='SVG 2 - UA (темна)')),
                        ('svg_2_world_light', models.TextField(blank=True, verbose_name='SVG 2 - World (світла)')),
                        ('svg_2_world_dark', models.TextField(blank=True, verbose_name='SVG 2 - World (темна)')),
                        ('svg_3_ua_light', models.TextField(blank=True, verbose_name='SVG 3 - UA (світла)')),
                        ('svg_3_ua_dark', models.TextField(blank=True, verbose_name='SVG 3 - UA (темна)')),
                        ('svg_3_world_light', models.TextField(blank=True, verbose_name='SVG 3 - World (світла)')),
                        ('svg_3_world_dark', models.TextField(blank=True, verbose_name='SVG 3 - World (темна)')),
                        ('is_active', models.BooleanField(default=True, verbose_name='Активно')),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                    ],
                    options={
                        'verbose_name': 'Секція 3',
                        'verbose_name_plural': '📖 Про нас → Секція 3',
                        'db_table': 'cms_about_section3',
                    },
                ),
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
                        ('svg_1_ua_light', models.TextField(blank=True, verbose_name='SVG 1 - UA (світла)')),
                        ('svg_1_ua_dark', models.TextField(blank=True, verbose_name='SVG 1 - UA (темна)')),
                        ('svg_1_world_light', models.TextField(blank=True, verbose_name='SVG 1 - World (світла)')),
                        ('svg_1_world_dark', models.TextField(blank=True, verbose_name='SVG 1 - World (темна)')),
                        ('svg_2_ua_light', models.TextField(blank=True, verbose_name='SVG 2 - UA (світла)')),
                        ('svg_2_ua_dark', models.TextField(blank=True, verbose_name='SVG 2 - UA (темна)')),
                        ('svg_2_world_light', models.TextField(blank=True, verbose_name='SVG 2 - World (світла)')),
                        ('svg_2_world_dark', models.TextField(blank=True, verbose_name='SVG 2 - World (темна)')),
                        ('svg_3_ua_light', models.TextField(blank=True, verbose_name='SVG 3 - UA (світла)')),
                        ('svg_3_ua_dark', models.TextField(blank=True, verbose_name='SVG 3 - UA (темна)')),
                        ('svg_3_world_light', models.TextField(blank=True, verbose_name='SVG 3 - World (світла)')),
                        ('svg_3_world_dark', models.TextField(blank=True, verbose_name='SVG 3 - World (темна)')),
                        ('svg_4_ua_light', models.TextField(blank=True, verbose_name='SVG 4 - UA (світла)')),
                        ('svg_4_ua_dark', models.TextField(blank=True, verbose_name='SVG 4 - UA (темна)')),
                        ('svg_4_world_light', models.TextField(blank=True, verbose_name='SVG 4 - World (світла)')),
                        ('svg_4_world_dark', models.TextField(blank=True, verbose_name='SVG 4 - World (темна)')),
                        ('svg_5_ua_light', models.TextField(blank=True, verbose_name='SVG 5 - UA (світла)')),
                        ('svg_5_ua_dark', models.TextField(blank=True, verbose_name='SVG 5 - UA (темна)')),
                        ('svg_5_world_light', models.TextField(blank=True, verbose_name='SVG 5 - World (світла)')),
                        ('svg_5_world_dark', models.TextField(blank=True, verbose_name='SVG 5 - World (темна)')),
                        ('svg_6_ua_light', models.TextField(blank=True, verbose_name='SVG 6 - UA (світла)')),
                        ('svg_6_ua_dark', models.TextField(blank=True, verbose_name='SVG 6 - UA (темна)')),
                        ('svg_6_world_light', models.TextField(blank=True, verbose_name='SVG 6 - World (світла)')),
                        ('svg_6_world_dark', models.TextField(blank=True, verbose_name='SVG 6 - World (темна)')),
                        ('is_active', models.BooleanField(default=True, verbose_name='Активно')),
                        ('updated_at', models.DateTimeField(auto_now=True)),
                    ],
                    options={
                        'verbose_name': 'Секція 4',
                        'verbose_name_plural': '📖 Про нас → Секція 4',
                        'db_table': 'cms_about_section4',
                    },
                ),
            ],
            database_operations=[
                # AboutSection3 - Add 12 grid SVG fields
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
                
                # AboutSection4 - Add 24 grid SVG fields
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
        ),
    ]
