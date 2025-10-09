# Generated manually for screenshot changes
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0002_material_s3_video_key_material_secure_video_enabled_and_more'),
    ]

    operations = [
        # Додати нові поля до Tag
        migrations.AddField(
            model_name='tag',
            name='tag_type',
            field=models.CharField(
                choices=[
                    ('interest', 'Інтерес користувача'),
                    ('category', 'Категорія контенту'),
                    ('general', 'Загальний тег'),
                ],
                default='general',
                max_length=20,
                db_index=True
            ),
        ),
        migrations.AddField(
            model_name='tag',
            name='display_order',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Порядок відображення (для interest type)'
            ),
        ),
        
        # Оновити Meta для Tag
        migrations.AlterModelOptions(
            name='tag',
            options={
                'ordering': ['display_order', 'name'],
                'verbose_name': 'Tag',
                'verbose_name_plural': 'Tags'
            },
        ),
        
        # Додати індекс
        migrations.AddIndex(
            model_name='tag',
            index=models.Index(fields=['tag_type', 'display_order'], name='tags_type_order_idx'),
        ),
        
        # Додати поле training_specialization до Course
        migrations.AddField(
            model_name='course',
            name='training_specialization',
            field=models.CharField(
                blank=True,
                choices=[
                    ('', 'Загальний'),
                    ('goalkeeper', 'Тренер воротарів'),
                    ('youth', 'Дитячий тренер'),
                    ('fitness', 'Тренер ЗФП'),
                    ('professional', 'Тренер професійних команд'),
                ],
                default='',
                help_text='Застосовується тільки для курсів категорії "Тренерство"',
                max_length=30,
                verbose_name='Спеціалізація тренера',
                db_index=True
            ),
        ),
        
        # Створити модель MonthlyQuote
        migrations.CreateModel(
            name='MonthlyQuote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expert_name', models.CharField(max_length=100, verbose_name='Імʼя експерта')),
                ('expert_role', models.CharField(max_length=150, verbose_name='Посада/роль')),
                ('expert_photo', models.ImageField(blank=True, upload_to='experts/monthly_quotes/', verbose_name='Фото експерта')),
                ('quote_text', models.TextField(verbose_name='Текст цитати')),
                ('month', models.DateField(help_text='Завжди 1-е число місяця (напр. 2025-10-01)', unique=True, verbose_name='Місяць')),
                ('is_active', models.BooleanField(default=True, help_text='Тільки одна цитата може бути активною для поточного місяця', verbose_name='Активна')),
                ('views_count', models.PositiveIntegerField(default=0)),
                ('last_displayed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Цитата місяця',
                'verbose_name_plural': 'Цитати місяця',
                'db_table': 'monthly_quotes',
                'ordering': ['-month'],
            },
        ),
        
        # Додати індекс для MonthlyQuote
        migrations.AddIndex(
            model_name='monthlyquote',
            index=models.Index(fields=['-month', 'is_active'], name='monthly_quotes_month_active_idx'),
        ),
    ]

