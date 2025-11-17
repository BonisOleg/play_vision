# Generated manually - Add UA/World dual content to HeroSlide

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0003_eventgridcell_pagesvg_trackingpixel_featuredcourse'),
    ]

    operations = [
        # Rename existing fields to _ua
        migrations.RenameField(
            model_name='heroslide',
            old_name='title',
            new_name='title_ua',
        ),
        migrations.RenameField(
            model_name='heroslide',
            old_name='subtitle',
            new_name='subtitle_ua',
        ),
        migrations.RenameField(
            model_name='heroslide',
            old_name='cta_text',
            new_name='cta_text_ua',
        ),
        
        # Add _world versions
        migrations.AddField(
            model_name='heroslide',
            name='title_world',
            field=models.CharField(blank=True, max_length=200, verbose_name='Title (World)'),
        ),
        migrations.AddField(
            model_name='heroslide',
            name='subtitle_world',
            field=models.CharField(blank=True, max_length=300, verbose_name='Subtitle (World)'),
        ),
        migrations.AddField(
            model_name='heroslide',
            name='cta_text_world',
            field=models.CharField(blank=True, max_length=50, verbose_name='CTA Text (World)'),
        ),
    ]

