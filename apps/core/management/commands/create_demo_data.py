"""
Management команда для створення demo даних для Play Vision
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Створює demo дані для всіх розділів платформи'
    
    def handle(self, *args, **options):
        self.stdout.write('🚀 Створення demo даних для Play Vision...')
        
        # Створення користувачів
        self.create_users()
        
        # Створення категорій та тегів
        self.create_categories_and_tags()
        
        # Створення курсів
        self.create_courses()
        
        # Створення планів підписок
        self.create_subscription_plans()
        
        # Створення івентів
        self.create_events()
        
        # Створення промокодів
        self.create_coupons()
        
        # AI конфігурація
        self.create_ai_config()
        
        self.stdout.write(
            self.style.SUCCESS('🎉 Demo дані успішно створені!')
        )
    
    def create_users(self):
        """Створення користувачів"""
        User = get_user_model()
        
        users_data = [
            {
                'email': 'admin@playvision.com',
                'password': 'admin123',
                'is_superuser': True,
                'first_name': 'Адміністратор',
                'last_name': 'Системи'
            },
            {
                'email': 'coach@playvision.com', 
                'password': 'coach123',
                'first_name': 'Олександр',
                'last_name': 'Тренеренко'
            },
            {
                'email': 'analyst@playvision.com',
                'password': 'analyst123', 
                'first_name': 'Максим',
                'last_name': 'Аналітик'
            }
        ]
        
        for user_data in users_data:
            if not User.objects.filter(email=user_data['email']).exists():
                is_super = user_data.pop('is_superuser', False)
                password = user_data.pop('password')
                
                # Додаємо username який дорівнює email
                user_data['username'] = user_data['email']
                
                if is_super:
                    user = User.objects.create_superuser(**user_data, password=password)
                else:
                    user = User.objects.create_user(**user_data, password=password)
                
                # Створення профіля
                from apps.accounts.models import Profile
                Profile.objects.get_or_create(
                    user=user,
                    defaults={
                        'first_name': user_data['first_name'],
                        'last_name': user_data['last_name'],
                        'completed_survey': True
                    }
                )
                self.stdout.write(f'✅ Користувач створений: {user.email}')
        
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
                self.stdout.write(f'✅ Категорія створена: {category.name}')
        
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
                self.stdout.write(f'✅ Тег створений: {tag.name}')
    
    def create_courses(self):
        """Створення курсів"""
        from apps.content.models import Course, Category, Tag
        
        courses_data = [
            {
                'title': 'Скаутинг молодих гравців',
                'slug': 'scouting-young-players',
                'category': 'analyst',
                'description': 'Повний курс по скаутингу молодих футболістів',
                'short_description': 'Навчіться професійно оцінювати молодих гравців',
                'difficulty': 'intermediate',
                'duration_minutes': 180,
                'price': Decimal('299.00'),
                'is_published': True,
                'is_featured': True,
                'tags': ['скаутинг', 'молодь', 'аналітик']
            },
            {
                'title': 'Тактика 4-3-3: Сучасний підхід',
                'slug': 'tactics-433-modern',
                'category': 'coach', 
                'description': 'Детальний розбір тактичної схеми 4-3-3',
                'short_description': 'Вивчіть всі нюанси популярної тактики',
                'difficulty': 'advanced',
                'duration_minutes': 240,
                'price': Decimal('399.00'),
                'is_published': True,
                'tags': ['тактика', 'тренер', 'професійний']
            },
            {
                'title': 'Харчування футболіста',
                'slug': 'football-nutrition',
                'category': 'nutrition',
                'description': 'Основи спортивного харчування для футболістів',
                'short_description': 'Правильне харчування - основа успіху',
                'difficulty': 'beginner',
                'duration_minutes': 120,
                'price': Decimal('199.00'),
                'is_published': True,
                'is_free': True,
                'tags': ['харчування', 'базовий']
            },
            {
                'title': 'Психологія переможця',
                'slug': 'winner-psychology',
                'category': 'psychology',
                'description': 'Ментальна підготовка футболістів',
                'short_description': 'Розвийте переможний менталітет',
                'difficulty': 'intermediate', 
                'duration_minutes': 150,
                'price': Decimal('249.00'),
                'is_published': True,
                'tags': ['психологія', 'ментальність']
            },
            {
                'title': 'Аналіз суперників',
                'slug': 'opponent-analysis',
                'category': 'analyst',
                'description': 'Методики аналізу команд-суперників',
                'short_description': 'Вивчіть слабкі та сильні сторони суперників', 
                'difficulty': 'advanced',
                'duration_minutes': 200,
                'price': Decimal('349.00'),
                'is_published': True,
                'tags': ['аналітик', 'тактика', 'професійний']
            }
        ]
        
        for course_data in courses_data:
            if not Course.objects.filter(slug=course_data['slug']).exists():
                tags = course_data.pop('tags', [])
                category_slug = course_data.pop('category')
                
                try:
                    category = Category.objects.get(slug=category_slug)
                    course_data['category'] = category
                    
                    course = Course.objects.create(**course_data)
                    
                    # Додавання тегів
                    for tag_name in tags:
                        try:
                            tag = Tag.objects.get(name=tag_name)
                            course.tags.add(tag)
                        except Tag.DoesNotExist:
                            pass
                    
                    self.stdout.write(f'✅ Курс створений: {course.title}')
                except Category.DoesNotExist:
                    self.stdout.write(f'❌ Категорія не знайдена: {category_slug}')
    
    def create_subscription_plans(self):
        """Створення планів підписок"""
        from apps.subscriptions.models import SubscriptionPlan as Plan
        
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
                self.stdout.write(f'✅ План підписки створений: {plan.name}')
    
    def create_events(self):
        """Створення івентів"""
        from apps.events.models import Event, Speaker
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        organizer = User.objects.filter(email='admin@playvision.com').first()
        
        if not organizer:
            return
        
        # Створення спікерів
        speakers_data = [
            {
                'first_name': 'Андрій',
                'last_name': 'Шевченко', 
                'email': 'sheva@playvision.com',
                'bio': 'Легенда українського футболу',
                'position': 'Тренер збірної України',
                'company': 'УАФ'
            },
            {
                'first_name': 'Олег',
                'last_name': 'Блохін',
                'email': 'blokhin@playvision.com', 
                'bio': 'Володар Золотого м\'яча',
                'position': 'Спортивний директор',
                'company': 'Динамо Київ'
            }
        ]
        
        speakers = []
        for speaker_data in speakers_data:
            speaker, created = Speaker.objects.get_or_create(
                email=speaker_data['email'],
                defaults=speaker_data
            )
            speakers.append(speaker)
            if created:
                self.stdout.write(f'✅ Спікер створений: {speaker.full_name}')
        
        # Створення івентів
        events_data = [
            {
                'title': 'Майстер-клас від Андрія Шевченка',
                'slug': 'shevchenko-masterclass',
                'event_type': 'workshop',
                'description': 'Унікальна можливість навчитися у легенди',
                'short_description': 'Ексклюзивний майстер-клас',
                'start_datetime': timezone.now() + timedelta(days=14),
                'end_datetime': timezone.now() + timedelta(days=14, hours=2),
                'location': 'Онлайн',
                'online_link': 'https://zoom.us/j/123456789',
                'max_attendees': 100,
                'price': Decimal('299.00'),
                'status': 'published',
                'is_featured': True,
                'speakers': [speakers[0]] if speakers else []
            },
            {
                'title': 'Форум тренерів 2024',
                'slug': 'coaches-forum-2024',
                'event_type': 'forum', 
                'description': 'Щорічний форум футбольних тренерів України',
                'short_description': 'Зустріч професіоналів галузі',
                'start_datetime': timezone.now() + timedelta(days=30),
                'end_datetime': timezone.now() + timedelta(days=31),
                'location': 'Київ, готель Дніпро',
                'max_attendees': 500,
                'price': Decimal('699.00'),
                'status': 'published',
                'requires_subscription': True,
                'speakers': speakers
            }
        ]
        
        for event_data in events_data:
            if not Event.objects.filter(slug=event_data['slug']).exists():
                speakers_list = event_data.pop('speakers', [])
                event_data['organizer'] = organizer
                
                event = Event.objects.create(**event_data)
                
                for speaker in speakers_list:
                    event.speakers.add(speaker)
                
                self.stdout.write(f'✅ Івент створений: {event.title}')
    
    def create_coupons(self):
        """Створення промокодів"""
        from apps.payments.models import Coupon
        
        coupons_data = [
            {
                'code': 'WELCOME10',
                'discount_type': 'percentage',
                'discount_value': Decimal('10'),
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=90),
                'min_amount': Decimal('100'),
                'max_uses': 100,
                'is_active': True
            },
            {
                'code': 'FIRST50',
                'discount_type': 'fixed',
                'discount_value': Decimal('50'),
                'valid_from': timezone.now(),
                'valid_until': timezone.now() + timedelta(days=30),
                'max_uses': 50,
                'once_per_user': True,
                'is_active': True
            }
        ]
        
        for coupon_data in coupons_data:
            coupon, created = Coupon.objects.get_or_create(
                code=coupon_data['code'],
                defaults=coupon_data
            )
            if created:
                self.stdout.write(f'✅ Промокод створений: {coupon.code}')
    
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
            self.stdout.write('✅ AI конфігурація створена')
        
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
                self.stdout.write(f'✅ AI політика створена: {policy.level}')
