#!/usr/bin/env python3

"""
Simple script to create test events
Run: python3 manage.py shell < create_data.py
"""

from django.utils import timezone
from datetime import timedelta
from apps.events.models import Event, Speaker
from apps.accounts.models import User
import random

print('Creating test data...')

# Get or create admin
organizer = User.objects.filter(username='admin').first()
if not organizer:
    organizer = User.objects.create_superuser('admin', 'admin@playvision.com', 'admin123')
    print('Created admin user')

# Create speakers
speakers_data = [
    {'first_name': 'Fabian', 'last_name': 'Otte', 'email': 'otte@playvision.com', 
     'position': 'Коучинг & Skill Acquisition', 'company': 'DFB Academy'},
    {'first_name': 'Adam', 'last_name': 'Owen', 'email': 'owen@playvision.com',
     'position': 'Методологія тренувань', 'company': 'Liverpool FC'},
    {'first_name': 'Hassane', 'last_name': 'Zouhal', 'email': 'zouhal@playvision.com',
     'position': 'Фізіологія', 'company': 'Rennes University'},
    {'first_name': 'Raphael', 'last_name': 'Villatore', 'email': 'villatore@playvision.com',
     'position': 'Нутриціологія', 'company': 'AC Milan'}
]

for data in speakers_data:
    speaker, created = Speaker.objects.get_or_create(email=data['email'], defaults=data)
    if created:
        print(f'Created speaker: {speaker.full_name}')

# Create events
now = timezone.now()
Event.objects.get_or_create(
    slug='forum-fff-5',
    defaults={
        'title': 'Форум футбольних фахівців 5',
        'short_description': 'Щорічна онлайн-подія для тренерів, аналітиків, менеджерів та психологів',
        'description': 'Форум для професійного розвитку та обміну досвідом.',
        'event_type': 'forum',
        'start_datetime': now + timedelta(days=1, hours=18),
        'end_datetime': now + timedelta(days=1, hours=21),
        'location': 'Онлайн',
        'online_link': 'https://zoom.us/j/123456789',
        'max_attendees': 500,
        'price': 1290,
        'is_featured': True,
        'status': 'published',
        'organizer': organizer,
        'tickets_sold': 125
    }
)

Event.objects.get_or_create(
    slug='masterclass-xg',
    defaults={
        'title': 'Майстер-клас xG',
        'short_description': 'Практичний майстер-клас з використання метрики xG',
        'description': 'Навчіться використовувати передову аналітику.',
        'event_type': 'workshop',
        'start_datetime': now + timedelta(days=2, hours=19),
        'end_datetime': now + timedelta(days=2, hours=21),
        'location': 'Онлайн',
        'max_attendees': 100,
        'price': 890,
        'status': 'published',
        'organizer': organizer,
        'tickets_sold': 45
    }
)

Event.objects.get_or_create(
    slug='roundtable-academies',
    defaults={
        'title': 'Круглий стіл: Академії',
        'short_description': 'Обговорення розвитку футбольних академій',
        'description': 'Зустріч керівників академій.',
        'event_type': 'seminar',
        'start_datetime': now + timedelta(days=3, hours=17),
        'end_datetime': now + timedelta(days=3, hours=19),
        'location': 'Онлайн',
        'max_attendees': 50,
        'is_free': True,
        'price': 0,
        'status': 'published',
        'organizer': organizer,
        'tickets_sold': 28
    }
)

Event.objects.get_or_create(
    slug='internship-dynamo',
    defaults={
        'title': 'Стажування у ФК Динамо',
        'short_description': 'Практичне стажування в академії',
        'description': 'Унікальна можливість стажування.',
        'event_type': 'internship',
        'start_datetime': now + timedelta(days=5, hours=10),
        'end_datetime': now + timedelta(days=5, hours=18),
        'location': 'м. Київ, вул. Грушевського 3',
        'max_attendees': 20,
        'price': 3500,
        'status': 'published',
        'organizer': organizer,
        'tickets_sold': 12
    }
)

print('Test data created!')
print('Admin login: username=admin, password=admin123')
