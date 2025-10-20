from django.core.management.base import BaseCommand
from apps.cms.models import HeroSlide


class Command(BaseCommand):
    help = 'Створити 6 hero слайдів згідно usertask.md'

    def handle(self, *args, **options):
        self.stdout.write('Створюємо hero слайди...')
        
        # 6 слайдів згідно usertask.md розділ 4, блок 1
        slides_data = [
            {
                'title': 'Ми відкрилися. Play Vision стартує!',
                'subtitle': 'Нова платформа для тренерів, аналітиків, гравців і менеджерів. Поєднуємо освіту, технології та футбольну культуру.',
                'badge': 'НОВИНА',
                'cta_text': 'Дізнатися більше',
                'cta_url': '/about/',
                'button_style': 'red',
                'background_style': 'white',
                'order': 1,
                'is_active': True,
            },
            {
                'title': 'Івенти',
                'subtitle': 'Форуми, воркшопи, практичні семінари, хакатони. Живе спілкування та реальні можливості.',
                'badge': '',
                'cta_text': 'Календар подій',
                'cta_url': '/events/',
                'button_style': 'white',
                'background_style': 'dark',
                'order': 2,
                'is_active': True,
            },
            {
                'title': 'Хаб знань. Долучайся першим.',
                'subtitle': 'Курси, відео, тренерські конспекти, бази вправ, статті. Освіта для тих, хто мислить у футболі.',
                'badge': '',
                'cta_text': 'Увійти до Хабу',
                'cta_url': '/hub/',
                'button_style': 'white-on-red',
                'background_style': 'red',
                'order': 3,
                'is_active': True,
            },
            {
                'title': 'Ментор-коучінг',
                'subtitle': 'Індивідуальний супровід спортсменів, тренерів і команд: ментальність, техніка, фізична й ігрова підготовка.',
                'badge': '',
                'cta_text': 'Обрати програму',
                'cta_url': '/mentor-coaching/',
                'button_style': 'black',
                'background_style': 'white',
                'order': 4,
                'is_active': True,
            },
            {
                'title': 'Про нас',
                'subtitle': 'Play Vision — команда експертів, що об\'єднує освіту, інновації та менторство. Ми створюємо нову культуру футбольного розвитку в Україні.',
                'badge': '',
                'cta_text': 'Познайомитися з нами',
                'cta_url': '/about/',
                'button_style': 'red',
                'background_style': 'white',
                'order': 5,
                'is_active': True,
            },
            {
                'title': 'Напрямки діяльності',
                'subtitle': 'Івенти, Ментор-коучінг, Хаб знань, Інновації і технології. Повна екосистема футбольного розвитку.',
                'badge': '',
                'cta_text': 'Дізнатися більше',
                'cta_url': '/about/',
                'button_style': 'black',
                'background_style': 'brand',
                'order': 6,
                'is_active': True,
            },
        ]
        
        for data in slides_data:
            slide, created = HeroSlide.objects.get_or_create(
                title=data['title'],
                defaults=data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Створено слайд: {data["title"]}'))
            else:
                # Оновити дані якщо слайд вже існує
                for key, value in data.items():
                    setattr(slide, key, value)
                slide.save()
                self.stdout.write(f'  Слайд вже існує (оновлено): {data["title"]}')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ Всі hero слайди створено!'))
        self.stdout.write('')
        self.stdout.write('ВАЖЛИВО:')
        self.stdout.write('  • Завантажте зображення для кожного слайду (1920x1080)')
        self.stdout.write('  • Використовуйте БІЛІ РАМКИ навколо банерів (НЕ заливку!)')
        self.stdout.write('  • На кожному слайді тільки ОДНА ЗЕЛЕНА кнопка зі стрілкою →')
        self.stdout.write('')
        self.stdout.write(f'  Всього слайдів: {HeroSlide.objects.filter(is_active=True).count()}')

