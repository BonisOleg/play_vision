"""
Management команда для оновлення посилань "Приєднатись до клубу" для курсів
Використання: python manage.py update_course_join_urls
"""

from django.core.management.base import BaseCommand
from django.db.models import Q
from apps.content.models import Course


class Command(BaseCommand):
    help = 'Оновлює посилання external_join_url для курсів з наданого списку'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Оновлення посилань для курсів...\n'))

        # Список курсів з точними назвами з бази даних та посиланнями
        # Примітка: "Імперія Ред Булл" з наданого списку відсутня в базі даних
        courses_data = [
            {
                'title': 'Соціальний та фінансовий капітал футболіста завдяки соцмережам',
                'url': 'https://edu.playvision.com.ua/o/CCD6YZ4xVnNr/payment/2756'
            },
            {
                'title': 'Індивідуальний аналіз і оцінювання гравців в збірній України',
                'url': 'https://edu.playvision.com.ua/o/CCD6YZ4xVnNr/payment/2756'
            },
            {
                'title': 'Комунікація та згуртованість команди в дитячо-юнацькому футболі',
                'url': 'https://edu.playvision.com.ua/o/Is1i7O4ulvgj/payment/2756'
            },
            {
                'title': 'Позиційна оборона і специфіка середньо-низького блоку',
                'url': 'https://edu.playvision.com.ua/o/1bY1atmict6m/payment/2756'
            },
            {
                'title': 'Емоційний інтелект тренера',
                'url': 'https://edu.playvision.com.ua/o/0IUPYkAlEpqe/payment/2756'
            },
            {
                'title': 'Модель гри чемпіона',
                'url': 'https://edu.playvision.com.ua/o/HqMSCKnKaaK2/payment/2756'
            },
            {
                'title': 'Особливість проведення УПЛ у військовий час',
                'url': 'https://edu.playvision.com.ua/o/E939NZ7IRFra/payment/2756'
            },
            {
                'title': 'Використання статистичних даних в сучасних реаліях',
                'url': 'https://edu.playvision.com.ua/o/M95GRqJjTxrH/payment/2756'
            },
            {
                'title': 'Манібол по-англійськи',
                'url': 'https://edu.playvision.com.ua/o/q6f4s6lyoEkr/payment/2756'
            },
            {
                'title': 'Філософія Пепа Гвардіоли',
                'url': 'https://edu.playvision.com.ua/o/jXXKQgmW6Yka/payment/2756'
            },
            {
                'title': 'Топ 30 аналітичних метрик',
                'url': 'https://edu.playvision.com.ua/o/ov3jglDQrZw8/payment/2756'
            },
            {
                'title': 'Сила тиші Анчелотті',
                'url': 'https://edu.playvision.com.ua/o/GXU0aCCKzuwU/payment/2756'
            },
            {
                'title': 'Революція Арріго Саккі',
                'url': 'https://edu.playvision.com.ua/o/9PBhWBEoeVlR/payment/2756'
            },
            {
                'title': 'Раціональна революція "Тулузи".',
                'url': 'https://edu.playvision.com.ua/o/Gxyb6cMaelrn/payment/2756'
            },
            {
                'title': 'Нелінійна педагогіка у футболі',
                'url': 'https://edu.playvision.com.ua/o/kSNblU1bG3S4/payment/2756'
            },
            {
                'title': 'Мікродозування силової роботи в футболі',
                'url': 'https://edu.playvision.com.ua/o/BsmkvT7AIi0P/payment/2756'
            },
            {
                'title': 'Мистецтво гри довгими передачами',
                'url': 'https://edu.playvision.com.ua/o/kYsDtPOpvEwY/payment/2756'
            },
            {
                'title': 'Методологія академії Аталанти',
                'url': 'https://edu.playvision.com.ua/o/YRxuRqGeb6oa/payment/2756'
            },
            {
                'title': 'Актуальні тактичні тенденції у футболі',
                'url': 'https://edu.playvision.com.ua/o/mXCgzkaYdK7l/payment/2756'
            },
            {
                'title': 'Тренерський менеджмент: як зібрати якісний штаб',
                'url': 'https://edu.playvision.com.ua/o/6IsrfUFfw11K/payment/2756'
            },
            {
                'title': 'Розуміння гри через Простір і Час: cуть концепції',
                'url': 'https://edu.playvision.com.ua/o/cw0EGXRvWJi3/payment/2756'
            },
            {
                'title': 'Розвиток структури клубу',
                'url': 'https://edu.playvision.com.ua/o/pPRcysR2AFyC/payment/2756'
            },
            {
                'title': 'Аналітика в сучасному футболі',
                'url': 'https://edu.playvision.com.ua/o/R7XqQIxM906t/payment/2756'
            },
            {
                'title': 'Особливості розвитку позиційної атаки і прогресії м\'яча',
                'url': 'https://edu.playvision.com.ua/o/h1n431tUoCe4/payment/2756'
            },
            {
                'title': 'Тактика в дитячому футболі: як підвести команду до гри 11х11',
                'url': 'https://edu.playvision.com.ua/o/VpISNWYJvgly/payment/2756'
            },
            {
                'title': 'Ментальні тренування молодих футболістів',
                'url': 'https://edu.playvision.com.ua/o/HhwORvfyKoa8/payment/2756'
            },
            {
                'title': 'Ігровий інтелект: як проходить процес прийняття рішень',
                'url': 'https://edu.playvision.com.ua/o/Qeg26loeSAjT/payment/2756'
            },
            {
                'title': 'Ключові моменти тактичної періодизації',
                'url': 'https://edu.playvision.com.ua/o/NEyT5sypb1jK/payment/2756'
            },
            {
                'title': 'Серія робочих блокнотів з психології',
                'url': 'https://edu.playvision.com.ua/o/pNqUoKGFFTaz/payment/2756'
            },
            {
                'title': 'Як організувати роботу селекційного відділу',
                'url': 'https://edu.playvision.com.ua/o/2gprlCYwG62j/payment/2756'
            },
            {
                'title': 'Розробка моделі гри: принципи та ключові чинники',
                'url': 'https://edu.playvision.com.ua/o/nfU2NQbJoYNA/payment/2756'
            },
            {
                'title': 'Структура vs Взаємодія: аналітичний розбір Positionism і Relationism',
                'url': 'https://edu.playvision.com.ua/o/nexniMFD8QXe/payment/2756'
            },
            {
                'title': 'Що ховається за глибинною обороною? Аналітичний розбір',
                'url': 'https://edu.playvision.com.ua/o/2VJSyxufuNqJ/payment/2756'
            },
            {
                'title': 'Комплексне формування гравця в сучасній футбольній академії',
                'url': 'https://edu.playvision.com.ua/o/A2t8GX0EmwNS/payment/2756'
            },
            {
                'title': 'Жіночий футбол в Україні: виклики та перспективи',
                'url': 'https://edu.playvision.com.ua/o/avNIkKTgpY5F/payment/2756'
            },
            {
                'title': 'Стандарти - як недооцінений інструмент в українському футболі',
                'url': 'https://edu.playvision.com.ua/o/fwsOV8rWtwM9/payment/2756'
            },
            {
                'title': 'Побудова команди з нуля в Україні та за кордоном',
                'url': 'https://edu.playvision.com.ua/o/4QgOwf6kLp44/payment/2756'
            },
            {
                'title': 'Скаутинг в ФК "Колос": специфіка діяльності селекційного відділу',
                'url': 'https://edu.playvision.com.ua/o/lqaKWirs8G1q/payment/2756'
            },
        ]

        updated_count = 0
        not_found = []
        multiple_matches = []

        for course_data in courses_data:
            title = course_data['title']
            url = course_data['url']

            # Спочатку точний пошук (case-insensitive)
            courses = Course.objects.filter(title__iexact=title)

            # Якщо не знайдено - частковий пошук
            if not courses.exists():
                courses = Course.objects.filter(title__icontains=title)

            if courses.count() == 0:
                not_found.append(title)
                self.stdout.write(
                    self.style.WARNING(f'  ⚠ Не знайдено: {title}')
                )
            elif courses.count() == 1:
                course = courses.first()
                old_url = course.external_join_url
                course.external_join_url = url
                course.save(update_fields=['external_join_url'])
                updated_count += 1
                
                if old_url:
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ Оновлено: {title}')
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f'  ✓ Додано: {title}')
                    )
            else:
                # Кілька співпадінь - використовуємо перший
                course = courses.first()
                old_url = course.external_join_url
                course.external_join_url = url
                course.save(update_fields=['external_join_url'])
                updated_count += 1
                multiple_matches.append({
                    'title': title,
                    'count': courses.count(),
                    'used': course.title
                })
                self.stdout.write(
                    self.style.WARNING(
                        f'  ⚠ Кілька співпадінь ({courses.count()}) для "{title}" - оновлено перший: "{course.title}"'
                    )
                )

        # Звіт
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS(f'\nОновлено курсів: {updated_count}'))
        
        if not_found:
            self.stdout.write(
                self.style.WARNING(f'\nНе знайдено курсів ({len(not_found)}):')
            )
            for title in not_found:
                self.stdout.write(f'  - {title}')
        
        if multiple_matches:
            self.stdout.write(
                self.style.WARNING(f'\nКілька співпадінь ({len(multiple_matches)}):')
            )
            for match in multiple_matches:
                self.stdout.write(
                    f'  - "{match["title"]}" → знайдено {match["count"]}, використано: "{match["used"]}"'
                )

        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('\nГотово!'))

