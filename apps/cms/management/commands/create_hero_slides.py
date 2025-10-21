from django.core.management.base import BaseCommand
from apps.cms.models import HeroSlide


class Command(BaseCommand):
    help = 'Створити 6 конкретних hero слайдів згідно usertask.md'

    def handle(self, *args, **options):
        self.stdout.write('Створюємо hero слайди...\n')
        
        slides_data = [
            {
                'title': 'Ми відкрилися. Play Vision стартує!',
                'subtitle': 'Нова платформа для тренерів, аналітиків, гравців і менеджерів. Поєднуємо освіту, технології та футбольну культуру.',
                'badge': 'НОВИНА',
                'cta_text': 'Дізнатися більше',
                'cta_url': '/about/',
                'order': 1,
                'is_active': True,
            },
            {
                'title': 'Івенти',
                'subtitle': 'Форуми, воркшопи, практичні семінари, хакатони. Живе спілкування та реальні можливості.',
                'badge': '',
                'cta_text': 'Календар подій',
                'cta_url': '/events/',
                'order': 2,
                'is_active': True,
            },
            {
                'title': 'Хаб знань. Долучайся першим.',
                'subtitle': 'Курси, відео, тренерські конспекти, бази вправ, статті. Освіта для тих, хто мислить у футболі.',
                'badge': '',
                'cta_text': 'Увійти до Хабу',
                'cta_url': '/hub/',
                'order': 3,
                'is_active': True,
            },
            {
                'title': 'Ментор-коучинг',
                'subtitle': 'Індивідуальний супровід спортсменів, тренерів і команд: ментальність, техніка, фізична й ігрова підготовка.',
                'badge': '',
                'cta_text': 'Обрати програму',
                'cta_url': '/mentor-coaching/',
                'order': 4,
                'is_active': True,
            },
            {
                'title': 'Про нас',
                'subtitle': 'Play Vision — команда експертів, що об\'єднує освіту, інновації та менторство. Ми створюємо нову культуру футбольного розвитку в Україні.',
                'badge': '',
                'cta_text': 'Познайомитися з нами',
                'cta_url': '/about/',
                'order': 5,
                'is_active': True,
            },
            {
                'title': 'Напрямки діяльності',
                'subtitle': 'Освіта • Івенти • Ментор-коучинг • Програма лояльності',
                'badge': '',
                'cta_text': 'Дізнатись більше',
                'cta_url': '/about/',
                'order': 6,
                'is_active': True,
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for data in slides_data:
            slide, created = HeroSlide.objects.update_or_create(
                order=data['order'],
                defaults=data
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Створено слайд #{data["order"]}: {data["title"]}'))
            else:
                updated_count += 1
                self.stdout.write(f'  Оновлено слайд #{data["order"]}: {data["title"]}')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✅ Готово! Створено: {created_count}, Оновлено: {updated_count}'))
        self.stdout.write('')
        self.stdout.write('💡 Тепер додайте зображення до слайдів через Django Admin:')
        self.stdout.write('   http://localhost:8000/admin/cms/heroslide/')
