"""
Management команда для створення основних програм (main courses)
Використання: python3 manage.py create_main_courses
"""

from django.core.management.base import BaseCommand
from apps.content.models import Course, Category


class Command(BaseCommand):
    help = 'Створює демо-дані для основних програм на головній сторінці'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Створення основних програм...'))

        # Отримуємо або створюємо категорії
        categories = {}
        category_names = {
            'psychology': 'Психологія',
            'analytics': 'Аналітика',
            'physiology': 'Фізіологія',
            'coaching': 'Тренерство',
        }

        for slug, name in category_names.items():
            category, created = Category.objects.get_or_create(
                slug=slug,
                defaults={'name': name}
            )
            categories[slug] = category
            if created:
                self.stdout.write(f'  ✓ Створена категорія: {name}')

        # Дані курсів відповідно до скріншота
        courses_data = [
            {
                'title': 'Тренерські принципи',
                'slug': 'trenerski-pryntsypy',
                'short_description': 'Основи ефективного коучингу та методології тренувального процесу.',
                'description': 'Комплексний курс для тренерів, який охоплює найважливіші аспекти тренерської роботи: від планування тренувань до роботи з командою.',
                'category': categories['coaching'],
                'difficulty': 'intermediate',
                'duration_minutes': 360,
                'price': 1500,
            },
            {
                'title': 'Спортивна фізіологія',
                'slug': 'sportyvna-fiziolohiya',
                'short_description': 'Науковий підхід до фізичної підготовки та відновлення спортсменів.',
                'description': 'Глибоке розуміння фізіологічних процесів в організмі спортсмена, методики тренувань та відновлення.',
                'category': categories['physiology'],
                'difficulty': 'advanced',
                'duration_minutes': 420,
                'price': 1800,
            },
            {
                'title': 'Скаутинг та аналітика',
                'slug': 'skauting-ta-analityka',
                'short_description': 'Сучасні методи аналізу гри та пошуку талантів.',
                'description': 'Професійний курс з використання даних та аналітики для покращення результатів команди та пошуку перспективних гравців.',
                'category': categories['analytics'],
                'difficulty': 'intermediate',
                'duration_minutes': 300,
                'price': 1600,
            },
            {
                'title': 'Лідерство в спорті',
                'slug': 'liderstvo-v-sporti',
                'short_description': 'Розвиток лідерських якостей та управління командою.',
                'description': 'Курс про розвиток лідерських навичок, мотивацію спортсменів та створення ефективної командної динаміки.',
                'category': categories['psychology'],
                'difficulty': 'intermediate',
                'duration_minutes': 240,
                'price': 1400,
            },
            {
                'title': 'Тактика та стратегія',
                'slug': 'taktyka-ta-stratehiya',
                'short_description': 'Тактичні схеми та стратегічне планування в футболі.',
                'description': 'Вивчення різних тактичних схем, стратегій гри та їх адаптація під конкретні ситуації.',
                'category': categories['coaching'],
                'difficulty': 'advanced',
                'duration_minutes': 480,
                'price': 2000,
            },
            {
                'title': 'Психологія спортсмена',
                'slug': 'psykholohiya-sportsmena',
                'short_description': 'Ментальна підготовка та психологічна підтримка гравців.',
                'description': 'Робота з психологічним станом спортсменів, подолання стресу та розвиток ментальної стійкості.',
                'category': categories['psychology'],
                'difficulty': 'beginner',
                'duration_minutes': 280,
                'price': 1200,
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
                    'is_free': False,
                    'requires_subscription': True,
                }
            )

            if created:
                created_count += 1
                self.stdout.write(f'  ✓ Створено: {course.title}')
            else:
                updated_count += 1
                self.stdout.write(f'  ↻ Оновлено: {course.title}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\nГотово! Створено: {created_count}, Оновлено: {updated_count}'
            )
        )

