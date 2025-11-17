"""
Management command для створення 6 featured курсів на головну сторінку
"""
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.content.models import Category, Course


class Command(BaseCommand):
    help = 'Створює 6 featured курсів для відображення на головній сторінці'

    def handle(self, *args, **options):
        self.stdout.write('Створення featured курсів...')

        # Отримати або створити категорії
        psychology_cat, _ = Category.objects.get_or_create(
            slug='psychology',
            defaults={'name': 'Психологія', 'icon': 'brain'}
        )
        analytics_cat, _ = Category.objects.get_or_create(
            slug='analytics',
            defaults={'name': 'Аналітика', 'icon': 'chart-bar'}
        )
        coaching_cat, _ = Category.objects.get_or_create(
            slug='coaching',
            defaults={'name': 'Тренерство', 'icon': 'users'}
        )
        physiology_cat, _ = Category.objects.get_or_create(
            slug='physiology',
            defaults={'name': 'Фізіологія', 'icon': 'heartbeat'}
        )

        courses_data = [
            {
                'title': 'Менталітет чемпіона',
                'slug': 'champion-mindset',
                'category': psychology_cat,
                'short_description': 'Формування переможного мислення',
                'description': 'Курс про розвиток психологічної стійкості та ментальної сили спортсменів',
                'price': Decimal('39.99'),
            },
            {
                'title': 'Скаутинг молодих гравців',
                'slug': 'youth-scouting',
                'category': analytics_cat,
                'short_description': 'Навчіться професійно оцінювати молодих гравців',
                'description': 'Професійний підхід до пошуку та оцінки молодих талантів у футболі',
                'price': Decimal('49.99'),
            },
            {
                'title': 'Тренерські принципи',
                'slug': 'coaching-principles',
                'category': coaching_cat,
                'short_description': 'Основи ефективного тренерства',
                'description': 'Фундаментальні принципи роботи тренера з командою та індивідуальними спортсменами',
                'price': Decimal('29.99'),
            },
            {
                'title': 'Спортивна фізіологія',
                'slug': 'sports-physiology',
                'category': physiology_cat,
                'short_description': 'Наука про тіло спортсмена',
                'description': 'Комплексний курс про фізіологічні процеси в організмі під час тренувань та змагань',
                'price': Decimal('44.99'),
            },
            {
                'title': 'Скаутинг та аналітика',
                'slug': 'scouting-analytics',
                'category': analytics_cat,
                'short_description': 'Сучасні методи скаутингу',
                'description': 'Використання аналітичних інструментів для ефективного скаутингу та оцінки гравців',
                'price': Decimal('54.99'),
            },
            {
                'title': 'Лідерство в спорті',
                'slug': 'sports-leadership',
                'category': psychology_cat,
                'short_description': 'Розвиток лідерських якостей',
                'description': 'Курс про розвиток лідерських навичок для капітанів команд та тренерів',
                'price': Decimal('34.99'),
            },
        ]

        created_count = 0
        updated_count = 0

        for course_data in courses_data:
            course, created = Course.objects.update_or_create(
                slug=course_data['slug'],
                defaults={
                    **course_data,
                    'is_published': True,
                    'is_featured': True,
                    'published_at': timezone.now()
                }
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Створено: {course.title}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Оновлено: {course.title}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Завершено! Створено: {created_count}, Оновлено: {updated_count}'
            )
        )

