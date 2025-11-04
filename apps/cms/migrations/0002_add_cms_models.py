from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HeroSlide',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Заголовок')),
                ('subtitle', models.CharField(blank=True, max_length=300, verbose_name='Підзаголовок')),
                ('badge', models.CharField(blank=True, help_text='Текст бейджу (ГОЛОВНЕ ЗАРАЗ)', max_length=50, verbose_name='Бейдж')),
                ('image', models.ImageField(blank=True, help_text='Рекомендований розмір: 1920×1080 px', upload_to='cms/hero/', verbose_name='Зображення')),
                ('video', models.FileField(blank=True, help_text='MP4 формат', upload_to='cms/hero/videos/', verbose_name='Відео')),
                ('cta_text', models.CharField(blank=True, max_length=50, verbose_name='Текст кнопки')),
                ('cta_url', models.CharField(blank=True, max_length=200, verbose_name='URL кнопки')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активний')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Hero Слайд',
                'verbose_name_plural': 'Hero Слайди',
                'db_table': 'cms_hero_slides',
                'ordering': ['order', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PageSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('page', models.CharField(default='home', max_length=50, verbose_name='Сторінка')),
                ('section_type', models.CharField(choices=[('hero', 'Hero'), ('featured_courses', 'Featured Курси'), ('courses', 'Курси'), ('mentor', 'Ментор коучинг'), ('experts', 'Експерти'), ('cta', 'Call to Action'), ('custom', 'Кастомна секція')], max_length=30, verbose_name='Тип секції')),
                ('title', models.CharField(blank=True, max_length=200, verbose_name='Заголовок')),
                ('subtitle', models.CharField(blank=True, max_length=300, verbose_name='Підзаголовок')),
                ('bg_image', models.ImageField(blank=True, upload_to='cms/sections/', verbose_name='Фонове зображення')),
                ('bg_color', models.CharField(default='#ffffff', max_length=7, verbose_name='Колір фону')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активна')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Секція сторінки',
                'verbose_name_plural': 'Секції сторінок',
                'db_table': 'cms_page_sections',
                'ordering': ['page', 'order'],
            },
        ),
        migrations.CreateModel(
            name='ExpertCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name="Ім'я")),
                ('position', models.CharField(max_length=150, verbose_name='Посада')),
                ('specialization', models.CharField(blank=True, max_length=200, verbose_name='Спеціалізація')),
                ('bio', models.TextField(blank=True, verbose_name='Біографія')),
                ('photo', models.ImageField(blank=True, help_text='Рекомендований розмір: 400×400 px', upload_to='cms/experts/', verbose_name='Фото')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активний')),
                ('show_on_homepage', models.BooleanField(default=True, verbose_name='Показувати на головній')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Експерт',
                'verbose_name_plural': 'Експерти',
                'db_table': 'cms_expert_cards',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='HexagonItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Назва')),
                ('icon_svg', models.TextField(help_text='Вставте SVG код іконки', verbose_name='SVG іконка')),
                ('description', models.TextField(blank=True, verbose_name='Опис')),
                ('color', models.CharField(default='#ff6b35', max_length=7, verbose_name='Колір')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активний')),
            ],
            options={
                'verbose_name': 'Hexagon елемент',
                'verbose_name_plural': 'Hexagon елементи',
                'db_table': 'cms_hexagon_items',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='SectionBlock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('block_type', models.CharField(choices=[('text', 'Текст'), ('image', 'Зображення'), ('card', 'Картка'), ('course_card', 'Картка курсу')], max_length=20, verbose_name='Тип блоку')),
                ('title', models.CharField(blank=True, max_length=200, verbose_name='Заголовок')),
                ('text', models.TextField(blank=True, verbose_name='Текст')),
                ('image', models.ImageField(blank=True, upload_to='cms/blocks/', verbose_name='Зображення')),
                ('cta_text', models.CharField(blank=True, max_length=50, verbose_name='Текст кнопки')),
                ('cta_url', models.CharField(blank=True, max_length=200, verbose_name='URL кнопки')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('section', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocks', to='cms.pagesection')),
            ],
            options={
                'verbose_name': 'Блок секції',
                'verbose_name_plural': 'Блоки секцій',
                'db_table': 'cms_section_blocks',
                'ordering': ['order'],
            },
        ),
    ]
