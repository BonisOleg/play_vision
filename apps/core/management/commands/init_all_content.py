from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Ініціалізувати весь початковий контент для Play Vision'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('ІНІЦІАЛІЗАЦІЯ КОНТЕНТУ PLAY VISION'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write('')

        commands = [
            ('create_hero_slides', '1. Hero слайди (6 штук)'),
            ('create_expert_quotes', '2. Цитати експертів (3 штуки)'),
            ('create_subscription_plans', '3. Тарифні плани (4 штуки)'),
            ('init_loyalty_rules', '4. Правила програми лояльності'),
        ]

        for command_name, description in commands:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING(f'▶ {description}'))
            self.stdout.write('-' * 60)
            try:
                call_command(command_name)
                self.stdout.write(self.style.SUCCESS(f'✅ {description} - виконано'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Помилка: {str(e)}'))
                self.stdout.write('')
                self.stdout.write(self.style.WARNING(f'⚠️  Команда {command_name} не знайдена або має помилки'))
                self.stdout.write(f'   Створіть її в apps/*/management/commands/{command_name}.py')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('ІНІЦІАЛІЗАЦІЯ ЗАВЕРШЕНА'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write('')
        self.stdout.write('📝 Наступні кроки:')
        self.stdout.write('   1. Додайте зображення через Django Admin')
        self.stdout.write('   2. Створіть курси з is_featured=True (мінімум 6)')
        self.stdout.write('   3. Створіть івенти (мінімум 5)')
        self.stdout.write('   4. Додайте експертів в CMS')
        self.stdout.write('')
        self.stdout.write('🌐 Django Admin:')
        self.stdout.write('   http://localhost:8000/admin/')
        self.stdout.write('')

