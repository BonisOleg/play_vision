"""
Management команда для завантаження бази знань AI
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.ai.services import KnowledgeBaseLoader
from apps.ai.models import KnowledgeBase
import os


class Command(BaseCommand):
    help = 'Завантажує файли з ai_knowledge_base директорії в базу знань AI'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--directory',
            type=str,
            default='ai_knowledge_base',
            help='Директорія з файлами бази знань (за замовчуванням: ai_knowledge_base)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистити існуючу базу знань перед завантаженням'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показати що буде завантажено без фактичного завантаження'
        )
    
    def handle(self, *args, **options):
        directory = options['directory']
        clear_existing = options['clear']
        dry_run = options['dry_run']
        
        # Повний шлях до директорії
        if not os.path.isabs(directory):
            directory = os.path.join(settings.BASE_DIR, directory)
        
        # Перевірка існування директорії
        if not os.path.exists(directory):
            self.stdout.write(
                self.style.ERROR(f'Директорія {directory} не існує')
            )
            return
        
        # Очищення існуючої бази знань
        if clear_existing and not dry_run:
            deleted_count = KnowledgeBase.objects.all().delete()[0]
            self.stdout.write(
                self.style.WARNING(f'Видалено {deleted_count} записів з бази знань')
            )
        
        # Отримання списку файлів
        files_to_load = []
        for filename in os.listdir(directory):
            if filename.endswith(('.md', '.txt')) and not filename.startswith('.'):
                files_to_load.append(filename)
        
        if not files_to_load:
            self.stdout.write(
                self.style.WARNING(f'Файли .md або .txt не знайдені в {directory}')
            )
            return
        
        self.stdout.write(f'Знайдено {len(files_to_load)} файлів для завантаження:')
        for filename in files_to_load:
            self.stdout.write(f'  - {filename}')
        
        if dry_run:
            self.stdout.write(
                self.style.SUCCESS('Dry run завершено. Використайте без --dry-run для фактичного завантаження.')
            )
            return
        
        # Завантаження файлів
        loader = KnowledgeBaseLoader()
        
        try:
            loaded_count = loader.load_from_directory(directory)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Успішно завантажено {loaded_count} документів в базу знань')
            )
            
            # Статистика
            total_entries = KnowledgeBase.objects.count()
            indexed_entries = KnowledgeBase.objects.filter(is_indexed=True).count()
            
            self.stdout.write(f'Загальна статистика бази знань:')
            self.stdout.write(f'  - Всього записів: {total_entries}')
            self.stdout.write(f'  - Проіндексовано: {indexed_entries}')
            
            # Статистика по рівнях доступу
            for level, display_name in KnowledgeBase._meta.get_field('access_level').choices:
                count = KnowledgeBase.objects.filter(access_level=level).count()
                self.stdout.write(f'  - {display_name}: {count}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Помилка завантаження: {str(e)}')
            )
