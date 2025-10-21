from django.core.management.base import BaseCommand
from apps.content.models import MonthlyQuote


class Command(BaseCommand):
    help = 'Створити 3 цитати експертів для карусель (Гвардіола, Моурінью, Анчелотті)'

    def handle(self, *args, **options):
        self.stdout.write('Створюємо цитати експертів...\n')
        
        quotes_data = [
            {
                'quote_text': 'Той, хто перестає вчитись, перестає бути тренером.',
                'author_name': 'Пеп Гвардіола',
                'author_title': 'Головний тренер Manchester City',
                'order': 1,
                'is_active': True,
            },
            {
                'quote_text': 'Якщо ти думаєш, що вже все знаєш — ти перестаєш рости.',
                'author_name': 'Жозе Моурінью',
                'author_title': 'Головний тренер',
                'order': 2,
                'is_active': True,
            },
            {
                'quote_text': 'Навчання — це не слабкість. Це означає амбіції.',
                'author_name': 'Карло Анчелотті',
                'author_title': 'Головний тренер Real Madrid',
                'order': 3,
                'is_active': True,
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for data in quotes_data:
            quote, created = MonthlyQuote.objects.update_or_create(
                author_name=data['author_name'],
                defaults=data
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Створено цитату: {data["author_name"]}'))
            else:
                updated_count += 1
                self.stdout.write(f'  Оновлено цитату: {data["author_name"]}')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✅ Готово! Створено: {created_count}, Оновлено: {updated_count}'))
        self.stdout.write('')
        self.stdout.write('💡 Додайте чорно-білі фото експертів через Django Admin:')
        self.stdout.write('   http://localhost:8000/admin/content/monthlyquote/')
        self.stdout.write('')
        self.stdout.write('📝 Рекомендовані розміри фото: 400x400px, чорно-біле')

