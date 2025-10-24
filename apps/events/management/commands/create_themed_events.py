from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.events.models import Event
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Видалити старі тестові дані та створити 9 тематичних подій'

    def handle(self, *args, **options):
        # Отримати першого суперюзера як організатора
        organizer = User.objects.filter(is_superuser=True).first()
        if not organizer:
            self.stdout.write(self.style.ERROR('Не знайдено суперюзера. Створіть спочатку адміністратора.'))
            return
        # Видалити всі події що містять "тестов" або "demo" в назві
        old_events = Event.objects.filter(
            title__icontains='тестов'
        ) | Event.objects.filter(
            title__icontains='demo'
        ) | Event.objects.filter(
            title__icontains='test'
        )
        
        count = old_events.count()
        if count > 0:
            old_events.delete()
            self.stdout.write(self.style.SUCCESS(f'✓ Видалено {count} старих тестових подій'))
        
        # Створити 9 тематичних подій
        now = timezone.now()
        events_data = [
            {
                'title': 'Форум футбольних фахівців 6',
                'slug': 'forum-futbolnyh-fahivtsiv-6',
                'event_type': 'forum',
                'event_category': 'football_experts_forum',
                'description': 'Щорічний форум для тренерів, аналітиків, менеджерів, нутриціологів та психологів. Головна подія року для футбольних професіоналів. Матеріали доступні у Хабі Знань після події.',
                'short_description': 'Головна подія року для футбольних професіоналів',
                'start_datetime': now + timedelta(days=30),
                'end_datetime': now + timedelta(days=30, hours=6),
                'location': 'Київ, НСК Олімпійський',
                'online_link': '',
                'is_featured': True,
                'is_free': False,
                'price': 5450,
                'max_attendees': 500,
                'status': 'published',
                'organizer': organizer,
            },
            {
                'title': 'Форум футбольних батьків: виховання чемпіонів',
                'slug': 'forum-futbolnyh-batkiv',
                'event_type': 'forum',
                'event_category': 'parents_forum',
                'description': 'Форум для батьків юних футболістів. Як підтримати дитину на шляху до професійної кар\'єри. Спілкування з експертами, психологами та успішними батьками.',
                'short_description': 'Форум для батьків юних футболістів',
                'start_datetime': now + timedelta(days=45),
                'end_datetime': now + timedelta(days=45, hours=4),
                'location': 'Online',
                'online_link': 'https://zoom.us/j/playvision-parents',
                'is_featured': True,
                'is_free': False,
                'price': 2500,
                'max_attendees': 200,
                'status': 'published',
                'organizer': organizer,
            },
            {
                'title': 'Стажування в академії Динамо Київ',
                'slug': 'stazhuvanna-dynamo',
                'event_type': 'internship',
                'event_category': 'internships',
                'description': 'Тижнева практика для молодих тренерів в академії ФК Динамо. Робота з дитячими групами під керівництвом досвідчених наставників. Отримайте реальний досвід роботи в професійному клубі.',
                'short_description': 'Тижнева практика в академії ФК Динамо',
                'start_datetime': now + timedelta(days=60),
                'end_datetime': now + timedelta(days=67),
                'location': 'Київ, база Динамо',
                'online_link': '',
                'is_featured': True,
                'is_free': False,
                'price': 15000,
                'max_attendees': 20,
                'status': 'published',
                'organizer': organizer,
            },
            {
                'title': 'Практичний семінар: сучасна тактика 3-4-3',
                'slug': 'seminar-taktyka-343',
                'event_type': 'seminar',
                'event_category': 'seminars_hackathons',
                'description': 'Інтенсивний семінар з розбором тактичної схеми 3-4-3. Відеоаналіз топ-клубів Європи, практичні вправи на полі, адаптація під різні вікові категорії.',
                'short_description': 'Інтенсивний семінар з тактики 3-4-3',
                'start_datetime': now + timedelta(days=15),
                'end_datetime': now + timedelta(days=15, hours=5),
                'location': 'Online',
                'online_link': 'https://zoom.us/j/playvision-tactics',
                'is_featured': False,
                'is_free': False,
                'price': 3200,
                'max_attendees': 100,
                'status': 'published',
                'organizer': organizer,
            },
            {
                'title': 'Хакатон: розробка тренувальних програм з AI',
                'slug': 'hakaton-ai-training',
                'event_type': 'seminar',
                'event_category': 'seminars_hackathons',
                'description': 'Дводенний хакатон для тренерів та аналітиків. Створюємо інноваційні тренувальні програми з використанням штучного інтелекту. Командна робота, менторство від експертів.',
                'short_description': 'Дводенний хакатон з AI для тренерів',
                'start_datetime': now + timedelta(days=90),
                'end_datetime': now + timedelta(days=92),
                'location': 'Київ, Unit City',
                'online_link': '',
                'is_featured': True,
                'is_free': False,
                'price': 8500,
                'max_attendees': 50,
                'status': 'published',
                'organizer': organizer,
            },
            {
                'title': 'Воркшоп: спортивна психологія для підлітків',
                'slug': 'workshop-psyhologya',
                'event_type': 'workshop',
                'event_category': 'psychology_workshops',
                'description': 'Практичний воркшоп зі спортивними психологами. Робота з мотивацією, стресом та емоційним інтелектом юних футболістів. Безкоштовна подія для тренерів та батьків.',
                'short_description': 'Воркшоп зі спортивної психології',
                'start_datetime': now + timedelta(days=20),
                'end_datetime': now + timedelta(days=20, hours=3),
                'location': 'Online',
                'online_link': 'https://zoom.us/j/playvision-psychology',
                'is_featured': False,
                'is_free': True,
                'price': 0,
                'max_attendees': 80,
                'status': 'published',
                'organizer': organizer,
            },
            {
                'title': 'Селекційний табір: пошук талантів U-15',
                'slug': 'camp-selekciya-u15',
                'event_type': 'conference',
                'event_category': 'selection_camps',
                'description': 'П\'ятиденний селекційний табір для гравців 2010 року народження. Оцінка технічних та фізичних якостей, відбір до академій. Участь скаутів провідних клубів України.',
                'short_description': 'Селекційний табір для U-15',
                'start_datetime': now + timedelta(days=75),
                'end_datetime': now + timedelta(days=80),
                'location': 'Конча-Заспа, тренувальна база',
                'online_link': '',
                'is_featured': True,
                'is_free': False,
                'price': 12000,
                'max_attendees': 60,
                'status': 'published',
                'organizer': organizer,
            },
            {
                'title': 'Онлайн-курс: основи скаутингу та аналітики',
                'slug': 'webinar-skauting-osnovy',
                'event_type': 'webinar',
                'event_category': 'online_webinars',
                'description': 'Тримісячний онлайн-курс для початківців скаутів. Методи оцінки гравців, робота з відео, складання звітів. 12 занять по 2 години, домашні завдання, сертифікат.',
                'short_description': 'Онлайн-курс основ скаутингу',
                'start_datetime': now + timedelta(days=10),
                'end_datetime': now + timedelta(days=100),
                'location': 'Online',
                'online_link': 'https://learn.playvision.com.ua/scouting',
                'is_featured': True,
                'is_free': False,
                'price': 9500,
                'max_attendees': 150,
                'status': 'published',
                'organizer': organizer,
            },
            {
                'title': 'Вебінар: нутриціологія в футболі',
                'slug': 'webinar-nutriciya',
                'event_type': 'webinar',
                'event_category': 'online_webinars',
                'description': 'Безкоштовний вебінар з експертом-нутриціологом. Харчування юних футболістів, добавки, режим дня. Практичні поради для батьків та тренерів.',
                'short_description': 'Безкоштовний вебінар з нутриціології',
                'start_datetime': now + timedelta(days=7),
                'end_datetime': now + timedelta(days=7, hours=2),
                'location': 'Online',
                'online_link': 'https://zoom.us/j/playvision-nutrition',
                'is_featured': False,
                'is_free': True,
                'price': 0,
                'max_attendees': 300,
                'status': 'published',
                'organizer': organizer,
            },
        ]
        
        created_count = 0
        for event_data in events_data:
            event, created = Event.objects.get_or_create(
                slug=event_data['slug'],
                defaults=event_data
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Створено: {event.title}'))
            else:
                self.stdout.write(f'  Подія вже існує: {event.title}')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✅ Створено {created_count} нових тематичних подій'))
        self.stdout.write(self.style.SUCCESS(f'📊 Всього подій в базі: {Event.objects.count()}'))

