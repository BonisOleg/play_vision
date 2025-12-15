# Generated manually
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0018_add_hub_hero_slides_4_5_and_backgrounds'),
    ]

    operations = [
        # CTA поля для слайда 1
        migrations.AddField(
            model_name='hubhero',
            name='cta_text_1_ua',
            field=models.CharField(blank=True, max_length=50, verbose_name='CTA текст 1 (Україна)'),
        ),
        migrations.AddField(
            model_name='hubhero',
            name='cta_text_1_world',
            field=models.CharField(blank=True, max_length=50, verbose_name='CTA текст 1 (Світ)'),
        ),
        migrations.AddField(
            model_name='hubhero',
            name='cta_url_1',
            field=models.CharField(blank=True, max_length=200, verbose_name='CTA URL 1'),
        ),
        # CTA поля для слайда 2
        migrations.AddField(
            model_name='hubhero',
            name='cta_text_2_ua',
            field=models.CharField(blank=True, max_length=50, verbose_name='CTA текст 2 (Україна)'),
        ),
        migrations.AddField(
            model_name='hubhero',
            name='cta_text_2_world',
            field=models.CharField(blank=True, max_length=50, verbose_name='CTA текст 2 (Світ)'),
        ),
        migrations.AddField(
            model_name='hubhero',
            name='cta_url_2',
            field=models.CharField(blank=True, max_length=200, verbose_name='CTA URL 2'),
        ),
        # CTA поля для слайда 3
        migrations.AddField(
            model_name='hubhero',
            name='cta_text_3_ua',
            field=models.CharField(blank=True, max_length=50, verbose_name='CTA текст 3 (Україна)'),
        ),
        migrations.AddField(
            model_name='hubhero',
            name='cta_text_3_world',
            field=models.CharField(blank=True, max_length=50, verbose_name='CTA текст 3 (Світ)'),
        ),
        migrations.AddField(
            model_name='hubhero',
            name='cta_url_3',
            field=models.CharField(blank=True, max_length=200, verbose_name='CTA URL 3'),
        ),
        # CTA поля для слайда 4
        migrations.AddField(
            model_name='hubhero',
            name='cta_text_4_ua',
            field=models.CharField(blank=True, max_length=50, verbose_name='CTA текст 4 (Україна)'),
        ),
        migrations.AddField(
            model_name='hubhero',
            name='cta_text_4_world',
            field=models.CharField(blank=True, max_length=50, verbose_name='CTA текст 4 (Світ)'),
        ),
        migrations.AddField(
            model_name='hubhero',
            name='cta_url_4',
            field=models.CharField(blank=True, max_length=200, verbose_name='CTA URL 4'),
        ),
        # CTA поля для слайда 5
        migrations.AddField(
            model_name='hubhero',
            name='cta_text_5_ua',
            field=models.CharField(blank=True, max_length=50, verbose_name='CTA текст 5 (Україна)'),
        ),
        migrations.AddField(
            model_name='hubhero',
            name='cta_text_5_world',
            field=models.CharField(blank=True, max_length=50, verbose_name='CTA текст 5 (Світ)'),
        ),
        migrations.AddField(
            model_name='hubhero',
            name='cta_url_5',
            field=models.CharField(blank=True, max_length=200, verbose_name='CTA URL 5'),
        ),
    ]

