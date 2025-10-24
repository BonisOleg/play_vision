from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.events.models import Event, Speaker
from apps.accounts.models import User
import random


class Command(BaseCommand):
    help = 'Creates test events for development'

    def handle(self, *args, **options):
        self.stdout.write('Creating test events...')
        
        # Get or create admin user as organizer
        try:
            organizer = User.objects.filter(is_superuser=True).first()
            if not organizer:
                organizer = User.objects.create_superuser(
                    username='admin',
                    email='admin@playvision.com',
                    password='admin123'
                )
                self.stdout.write(self.style.SUCCESS(f'Created admin user: {organizer.username}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Using existing admin user: {organizer.username}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error getting organizer: {e}'))
            return
        
        # Create speakers
        speakers_data = [
            {
                'first_name': 'Fabian',
                'last_name': 'Otte',
                'email': 'otte@playvision.com',
                'position': 'Коучинг & Skill Acquisition',
                'company': 'DFB Academy',
                'bio': 'Експерт з розвитку навичок та коучингу молодих футболістів'
            },
            {
                'first_name': 'Adam',
                'last_name': 'Owen',
                'email': 'owen@playvision.com',
                'position': 'Методологія тренувань',
                'company': 'Liverpool FC',
                'bio': 'Спеціаліст з фізичної підготовки та методології тренувань'
            },
            {
                'first_name': 'Hassane',
                'last_name': 'Zouhal',
                'email': 'zouhal@playvision.com',
                'position': 'Фізіологія',
                'company': 'Rennes University',
                'bio': 'Професор спортивної фізіології'
            },
            {
                'first_name': 'Raphael',
                'last_name': 'Villatore',
                'email': 'villatore@playvision.com',
                'position': 'Нутриціологія',
                'company': 'AC Milan',
                'bio': 'Експерт з спортивного харчування'
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
                self.stdout.write(self.style.SUCCESS(f'Created speaker: {speaker.full_name}'))
        
        # Create events
        now = timezone.now()
        # Знайти наступний понеділок
        days_ahead = 0 - now.weekday()  # 0 = Monday
        if days_ahead <= 0:
            days_ahead += 7
        next_monday = now + timedelta(days=days_ahead)
        
        events_data = [
            {
                'title': 'Форум футбольних фахівців 5',
                'slug': 'forum-fff-5',
                'short_description': 'Щорічна онлайн-подія для тренерів, аналітиків, менеджерів та психологів',
                'description': '''
                Форум футбольних фахівців 5 — це унікальна можливість для професійного розвитку та обміну досвідом.
                
                На форумі ви дізнаєтесь:
                - Сучасні методики тренувань молодих талантів
                - Підходи до скаутингу та оцінки гравців
                - Психологічні аспекти роботи з командою
                - Інноваційні підходи до фізичної підготовки
                
                Приєднуйтесь до спільноти професіоналів!
                ''',
                'event_type': 'forum',
                'event_category': 'football_experts_forum',
                'start_datetime': next_monday.replace(hour=18, minute=0, second=0, microsecond=0),
                'end_datetime': next_monday.replace(hour=21, minute=0, second=0, microsecond=0),
                'location': 'Онлайн',
                'online_link': 'https://zoom.us/j/123456789',
                'max_attendees': 500,
                'price': 1290,
                'is_featured': True,
                'requires_subscription': True
            },
            {
                'title': 'Майстер-клас xG: аналіз очікуваних голів',
                'slug': 'masterclass-xg',
                'short_description': 'Практичний майстер-клас з використання метрики xG в аналізі матчів',
                'description': '''
                Навчіться використовувати передову аналітику для оцінки ефективності команд та гравців.
                
                Програма майстер-класу:
                - Основи метрики xG
                - Інструменти для збору даних
                - Практичні кейси аналізу
                - Створення звітів для тренерів
                ''',
                'event_type': 'workshop',
                'event_category': 'seminars_hackathons',
                'start_datetime': (next_monday + timedelta(days=1)).replace(hour=19, minute=0, second=0, microsecond=0),
                'end_datetime': (next_monday + timedelta(days=1)).replace(hour=21, minute=0, second=0, microsecond=0),
                'location': 'Онлайн',
                'online_link': 'https://zoom.us/j/987654321',
                'max_attendees': 100,
                'price': 890,
                'is_free': False
            },
            {
                'title': 'Круглий стіл: Розвиток академій в Україні',
                'slug': 'roundtable-academies',
                'short_description': 'Обговорення актуальних питань розвитку футбольних академій',
                'description': '''
                Зустріч керівників провідних академій України для обговорення:
                - Стандарти підготовки молодих гравців
                - Інфраструктура та фінансування
                - Співпраця з професійними клубами
                - Міжнародний досвід
                ''',
                'event_type': 'seminar',
                'event_category': 'seminars_hackathons',
                'start_datetime': (next_monday + timedelta(days=2)).replace(hour=17, minute=0, second=0, microsecond=0),
                'end_datetime': (next_monday + timedelta(days=2)).replace(hour=19, minute=0, second=0, microsecond=0),
                'location': 'Онлайн',
                'max_attendees': 50,
                'price': 0,
                'is_free': True
            },
            {
                'title': 'Стажування у ФК "Динамо" Київ',
                'slug': 'internship-dynamo',
                'short_description': 'Практичне стажування в академії провідного клубу України',
                'description': '''
                Унікальна можливість пройти стажування в академії ФК "Динамо" Київ.
                
                Що включає програма:
                - Спостереження за тренувальним процесом
                - Участь у плануванні тренувань
                - Робота з молодіжними командами
                - Сертифікат про проходження стажування
                ''',
                'event_type': 'internship',
                'event_category': 'internships',
                'start_datetime': (next_monday + timedelta(days=3)).replace(hour=10, minute=0, second=0, microsecond=0),
                'end_datetime': (next_monday + timedelta(days=3)).replace(hour=18, minute=0, second=0, microsecond=0),
                'location': 'м. Київ, вул. Грушевського 3',
                'max_attendees': 20,
                'price': 3500,
                'requires_approval': True
            },
            {
                'title': 'Q&A зі скаутом топ-клубу',
                'slug': 'qa-scout',
                'short_description': 'Відверта розмова з професійним скаутом європейського клубу',
                'description': '''
                Ексклюзивна онлайн-зустріч зі скаутом, який працює в системі топ-клубів Європи.
                
                Теми для обговорення:
                - Що шукають скаути в молодих гравцях
                - Технології в скаутингу
                - Помилки при оцінці талантів
                - Кар\'єрні поради
                ''',
                'event_type': 'webinar',
                'event_category': 'online_webinars',
                'start_datetime': (next_monday + timedelta(days=4)).replace(hour=18, minute=30, second=0, microsecond=0),
                'end_datetime': (next_monday + timedelta(days=4)).replace(hour=20, minute=0, second=0, microsecond=0),
                'location': 'Онлайн',
                'max_attendees': 200,
                'price': 590
            },
            {
                'title': 'Практикум GPS-даних в футболі',
                'slug': 'practicum-gps',
                'short_description': 'Практичне заняття з аналізу GPS-даних гравців',
                'description': '''
                Навчіться використовувати GPS-трекери для оптимізації тренувального процесу.
                
                Практичні навички:
                - Налаштування обладнання
                - Збір та інтерпретація даних
                - Планування навантажень
                - Попередження травм
                ''',
                'event_type': 'workshop',
                'event_category': 'seminars_hackathons',
                'start_datetime': (next_monday + timedelta(days=10)).replace(hour=12, minute=0, second=0, microsecond=0),
                'end_datetime': (next_monday + timedelta(days=10)).replace(hour=16, minute=0, second=0, microsecond=0),
                'location': 'м. Львів, стадіон "Арена Львів"',
                'max_attendees': 30,
                'price': 1500
            },
            {
                'title': 'Менторинг 1:1 з експертом',
                'slug': 'mentoring-1-1',
                'short_description': 'Індивідуальна консультація з обраним експертом',
                'description': '''
                Персональна годинна сесія з експертом у вибраній області:
                - Тренерська діяльність
                - Спортивний менеджмент
                - Аналітика даних
                - Психологія спорту
                ''',
                'event_type': 'seminar',
                'event_category': 'psychology_workshops',
                'start_datetime': (next_monday + timedelta(days=5)).replace(hour=15, minute=0, second=0, microsecond=0),
                'end_datetime': (next_monday + timedelta(days=5)).replace(hour=16, minute=0, second=0, microsecond=0),
                'location': 'Онлайн',
                'max_attendees': 1,
                'price': 2500
            },
            {
                'title': 'Форум футбольних батьків 2',
                'slug': 'forum-parents-2',
                'short_description': 'Освітня подія для батьків юних футболістів',
                'description': '''
                Дізнайтеся, як правильно підтримувати дитину в спортивній кар'єрі.
                
                Основні теми:
                - Психологічна підтримка юного спортсмена
                - Баланс між спортом та навчанням
                - Харчування та режим дня
                - Комунікація з тренерами
                ''',
                'event_type': 'forum',
                'event_category': 'parents_forum',
                'start_datetime': (next_monday + timedelta(days=6)).replace(hour=17, minute=0, second=0, microsecond=0),
                'end_datetime': (next_monday + timedelta(days=6)).replace(hour=20, minute=0, second=0, microsecond=0),
                'location': 'м. Київ, НСК "Олімпійський" (гібридний формат)',
                'online_link': 'https://zoom.us/j/111222333',
                'max_attendees': 300,
                'price': 0,
                'is_free': True
            },
            {
                'title': 'Лекція з психологом: мотивація команди',
                'slug': 'lecture-psychology',
                'short_description': 'Практичні інструменти роботи з мотивацією гравців',
                'description': '''
                Спортивний психолог поділиться досвідом роботи з професійними командами.
                
                Ви дізнаєтесь:
                - Типи мотивації спортсменів
                - Робота з емоційним вигоранням
                - Командна динаміка
                - Індивідуальний підхід
                ''',
                'event_type': 'webinar',
                'event_category': 'psychology_workshops',
                'start_datetime': (next_monday + timedelta(days=7)).replace(hour=19, minute=0, second=0, microsecond=0),
                'end_datetime': (next_monday + timedelta(days=7)).replace(hour=21, minute=0, second=0, microsecond=0),
                'location': 'Онлайн',
                'max_attendees': 150,
                'price': 750
            },
            {
                'title': 'Менеджмент у футболі — семінар',
                'slug': 'management-seminar',
                'short_description': 'Основи спортивного менеджменту для початківців',
                'description': '''
                Комплексний семінар для тих, хто хоче розвиватися в спортивному менеджменті.
                
                Модулі програми:
                - Структура футбольного клубу
                - Фінансовий менеджмент
                - Маркетинг та PR
                - Робота з агентами
                ''',
                'event_type': 'seminar',
                'event_category': 'seminars_hackathons',
                'start_datetime': (next_monday + timedelta(days=14)).replace(hour=12, minute=0, second=0, microsecond=0),
                'end_datetime': (next_monday + timedelta(days=14)).replace(hour=18, minute=0, second=0, microsecond=0),
                'location': 'м. Дніпро, готель "Україна"',
                'max_attendees': 80,
                'price': 1800,
                'tickets_sold': 45
            },
            {
                'title': 'Форум футбольних фахівців 6',
                'slug': 'forum-fff-6',
                'short_description': 'Гібридний формат • листопад • теми: перехідні фази, розвиток U15-U19, комунікація штабу',
                'description': '''
                Наступна велика подія для футбольних професіоналів з можливістю участі офлайн та онлайн.
                
                Головні спікери та теми будуть оголошені найближчим часом.
                Слідкуйте за оновленнями!
                ''',
                'event_type': 'forum',
                'event_category': 'football_experts_forum',
                'start_datetime': (next_monday + timedelta(days=45)).replace(hour=10, minute=0, second=0, microsecond=0),
                'end_datetime': (next_monday + timedelta(days=45)).replace(hour=18, minute=0, second=0, microsecond=0),
                'location': 'м. Київ, Конгрес-хол (гібридний формат)',
                'max_attendees': 1000,
                'price': 2500,
                'is_featured': True,
                'status': 'published'
            }
        ]
        
        for event_data in events_data:
            # Add organizer
            event_data['organizer'] = organizer
            
            # Extract speakers assignment
            speakers_to_add = []
            if 'forum' in event_data['slug']:
                speakers_to_add = speakers[:4]  # All speakers for forums
            elif 'psychology' in event_data['slug']:
                speakers_to_add = [speakers[2]]  # Psychology speaker
            elif 'gps' in event_data['slug'] or 'xg' in event_data['slug']:
                speakers_to_add = [speakers[1]]  # Analytics speaker
            
            # Remove speakers from event_data to avoid error
            if 'speakers' in event_data:
                del event_data['speakers']
                
            # Create event
            event, created = Event.objects.get_or_create(
                slug=event_data['slug'],
                defaults=event_data
            )
            
            # Add speakers after creation
            if speakers_to_add:
                event.speakers.set(speakers_to_add)
            
            # Set random tickets sold
            if not hasattr(event, 'tickets_sold') or event.tickets_sold == 0:
                max_sold = max(0, event.max_attendees - 10)
                if max_sold > 10:
                    event.tickets_sold = random.randint(10, min(max_sold, 100))
                else:
                    event.tickets_sold = random.randint(0, max(0, event.max_attendees // 2))
                event.save()
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created event: {event.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'Event already exists: {event.title}'))
        
        self.stdout.write(self.style.SUCCESS('\nTest events created successfully!'))
        self.stdout.write(self.style.SUCCESS(f'Admin login: username=admin, password=admin123'))
