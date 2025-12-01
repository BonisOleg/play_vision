# Migration to add grid SVG fields to AboutSection3 and AboutSection4

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0016_fix_experts_visibility'),
    ]

    operations = [
        # AboutSection3 - Add 12 grid SVG fields (3 SVG × 4 versions each)
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
        
        # AboutSection4 - Add 24 grid SVG fields (6 SVG × 4 versions each)
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
    ]

