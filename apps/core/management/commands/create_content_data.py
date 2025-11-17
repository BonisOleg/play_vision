"""
Management команда для створення тільки контентних даних
Використовується коли користувачі вже створені
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Створює тільки контентні дані (категорії, курси, івенти)'
    
    def handle(self, *args, **options):
        self.stdout.write('📚 Створення контентних даних...')
        
        # Створення категорій та тегів
        self.create_categories_and_tags()
        
        # Створення курсів
        self.create_courses()
        
        # Створення планів підписок
        self.create_subscription_plans()
        
        # AI конфігурація
        self.create_ai_config()
        
        self.stdout.write(
            self.style.SUCCESS('✅ Контентні дані створені!')
        )
    
    def create_categories_and_tags(self):
        """Створення категорій та тегів"""
        from apps.content.models import Category, Tag
        
        categories_data = [
            {'name': 'Тренер', 'slug': 'coach', 'icon': '⚽', 'description': 'Курси для тренерів'},
            {'name': 'Аналітик', 'slug': 'analyst', 'icon': '📊', 'description': 'Аналітика в футболі'},
            {'name': 'Нутриціологія', 'slug': 'nutrition', 'icon': '🥗', 'description': 'Харчування спортсменів'},
            {'name': 'Психологія', 'slug': 'psychology', 'icon': '🧠', 'description': 'Спортивна психологія'},
            {'name': 'Менеджмент', 'slug': 'management', 'icon': '👔', 'description': 'Управління в футболі'},
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f'✅ Категорія: {category.name}')
        
        tags_data = [
            'тренер', 'аналітик', 'тактика', 'фізична підготовка', 
            'психологія', 'харчування', 'скаутинг', 'молодь',
            'професійний', 'базовий', 'експерт', 'початківець'
        ]
        
        for tag_name in tags_data:
            tag, created = Tag.objects.get_or_create(
                name=tag_name,
                defaults={'slug': tag_name.replace(' ', '-')}
            )
            if created:
                self.stdout.write(f'✅ Тег: {tag.name}')
    
    def create_courses(self):
        """Створення курсів"""
        from apps.content.models import Course, Category, Tag
        
        courses_data = [
            {
                'title': 'Скаутинг молодих гравців',
                'slug': 'scouting-young-players',
                'category': 'analyst',
                'description': 'Повний курс по скаутингу молодих футболістів. Вивчіть як професійно оцінювати потенціал молодих гравців, використовуючи сучасні методи аналізу.',
                'short_description': 'Навчіться професійно оцінювати молодих гравців',
                'price': Decimal('299.00'),
                'is_published': True,
                'is_featured': True,
                'tags': ['скаутинг', 'молодь', 'аналітик']
            },
            {
                'title': 'Тактика 4-3-3: Сучасний підхід',
                'slug': 'tactics-433-modern',
                'category': 'coach', 
                'description': 'Детальний розбір тактичної схеми 4-3-3 в сучасному футболі. Принципи гри в атаці та обороні, варіації схеми.',
                'short_description': 'Вивчіть всі нюанси популярної тактики',
                'price': Decimal('399.00'),
                'is_published': True,
                'tags': ['тактика', 'тренер', 'професійний']
            },
            {
                'title': 'Харчування футболіста',
                'slug': 'football-nutrition',
                'category': 'nutrition',
                'description': 'Основи спортивного харчування для футболістів. Як правильно харчуватися до, під час та після тренувань і матчів.',
                'short_description': 'Правильне харчування - основа успіху',
                'price': Decimal('199.00'),
                'is_published': True,
                'is_free': True,
                'tags': ['харчування', 'базовий']
            },
            {
                'title': 'Психологія переможця',
                'slug': 'winner-psychology',
                'category': 'psychology',
                'description': 'Ментальна підготовка футболістів. Розвиток впевненості, концентрації та стресостійкості.',
                'short_description': 'Розвийте переможний менталітет',
                'price': Decimal('249.00'),
                'is_published': True,
                'tags': ['психологія', 'ментальність']
            },
            {
                'title': 'Аналіз суперників',
                'slug': 'opponent-analysis',
                'category': 'analyst',
                'description': 'Методики аналізу команд-суперників. Як підготувати детальний звіт про сильні та слабкі сторони команди.',
                'short_description': 'Вивчіть слабкі та сильні сторони суперників', 
                'price': Decimal('349.00'),
                'is_published': True,
                'tags': ['аналітик', 'тактика', 'професійний']
            },
            {
                'title': 'Фізична підготовка гравців',
                'slug': 'physical-training',
                'category': 'coach',
                'description': 'Сучасні методи фізичної підготовки футболістів. Планування навантажень, відновлення.',
                'short_description': 'Комплексна фізична підготовка',
                'price': Decimal('279.00'),
                'is_published': True,
                'tags': ['фізична підготовка', 'тренер']
            },
            {
                'title': 'Менталітет чемпіона',
                'slug': 'champion-mindset', 
                'category': 'psychology',
                'description': 'Психологічні аспекти досягнення високих результатів в футболі.',
                'short_description': 'Формування переможного мислення',
                'price': Decimal('329.00'),
                'is_published': True,
                'is_featured': True,
                'tags': ['психологія', 'професійний']
            }
        ]
        
        for course_data in courses_data:
            if not Course.objects.filter(slug=course_data['slug']).exists():
                # Видаляємо tags, оскільки Course не має цього поля
                course_data.pop('tags', [])
                category_slug = course_data.pop('category')
                
                try:
                    category = Category.objects.get(slug=category_slug)
                    course_data['category'] = category
                    
                    course = Course.objects.create(**course_data)
                    
                    self.stdout.write(f'✅ Курс: {course.title}')
                except Category.DoesNotExist:
                    self.stdout.write(f'❌ Категорія не знайдена: {category_slug}')
    
    def create_subscription_plans(self):
        """Створення планів підписок"""
        from apps.subscriptions.models import Plan
        
        plans_data = [
            {
                'name': 'Базовий місяць',
                'slug': 'basic-month',
                'duration': '1_month',
                'duration_months': 1,
                'price': Decimal('199.00'),
                'features': ['Доступ до базових курсів', 'Форум спільноти'],
                'is_popular': False
            },
            {
                'name': 'Стандарт 3 місяці', 
                'slug': 'standard-3months',
                'duration': '3_months',
                'duration_months': 3,
                'price': Decimal('499.00'),
                'features': ['Всі курси', 'Івенти зі знижкою', 'Персональна підтримка'],
                'is_popular': True,
                'badge_text': 'Найпопулярніший'
            },
            {
                'name': 'Професійний рік',
                'slug': 'pro-year', 
                'duration': '12_months',
                'duration_months': 12,
                'price': Decimal('1599.00'),
                'features': ['Все включено', 'Безлімітні івенти', 'Персональні консультації'],
                'event_tickets_balance': 12,
                'discount_percentage': 20
            }
        ]
        
        for plan_data in plans_data:
            plan, created = Plan.objects.get_or_create(
                slug=plan_data['slug'],
                defaults=plan_data
            )
            if created:
                self.stdout.write(f'✅ План: {plan.name}')
    
    def create_ai_config(self):
        """Створення AI конфігурації"""
        from apps.ai.models import AIConfiguration, AIAccessPolicy
        
        # AI конфігурація
        config, created = AIConfiguration.objects.get_or_create(
            id=1,
            defaults={
                'llm_provider': 'openai',
                'llm_model': 'gpt-3.5-turbo',
                'is_enabled': True,
                'maintenance_mode': False
            }
        )
        if created:
            self.stdout.write('✅ AI конфігурація')
        
        # Політики доступу AI
        policies_data = [
            {
                'level': 'guest',
                'max_response_length': 200,
                'max_queries_per_day': 3,
                'max_queries_per_hour': 1,
                'cta_message': 'Зареєструйтесь для більшого доступу'
            },
            {
                'level': 'registered', 
                'max_response_length': 500,
                'max_queries_per_day': 10,
                'max_queries_per_hour': 5,
                'include_links': True,
                'show_previews': True,
                'cta_message': 'Оформіть підписку для експертних відповідей'
            },
            {
                'level': 'subscriber_l1',
                'max_response_length': 1000,
                'max_queries_per_day': 50,
                'max_queries_per_hour': 20,
                'include_links': True,
                'show_previews': True,
                'access_premium_content': True
            }
        ]
        
        for policy_data in policies_data:
            policy, created = AIAccessPolicy.objects.get_or_create(
                level=policy_data['level'],
                defaults=policy_data
            )
            if created:
                self.stdout.write(f'✅ AI політика: {policy.level}')
