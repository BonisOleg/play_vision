"""
Management команда для індексування курсів в базу знань AI
"""
from django.core.management.base import BaseCommand
from apps.content.models import Course
from apps.ai.services import KnowledgeBaseLoader


class Command(BaseCommand):
    help = 'Індексує курси в базу знань AI для покращення відповідей'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--course-id',
            type=int,
            help='Індексувати конкретний курс за ID'
        )
        parser.add_argument(
            '--published-only',
            action='store_true',
            help='Індексувати тільки опубліковані курси'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Очистити існуючі записи курсів перед індексуванням'
        )
    
    def handle(self, *args, **options):
        course_id = options.get('course_id')
        published_only = options['published_only']
        clear_existing = options['clear_existing']
        
        loader = KnowledgeBaseLoader()
        
        # Очищення існуючих записів курсів
        if clear_existing:
            from apps.ai.models import KnowledgeBase
            deleted = KnowledgeBase.objects.filter(
                content_type__in=['course', 'lesson']
            ).delete()
            self.stdout.write(
                self.style.WARNING(f'Видалено {deleted[0]} записів курсів з бази знань')
            )
        
        # Індексування конкретного курсу
        if course_id:
            try:
                course = Course.objects.get(id=course_id)
                success = loader.index_course_content(course_id)
                
                if success:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Курс "{course.title}" успішно проіндексований')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'❌ Помилка індексування курсу "{course.title}"')
                    )
                return
                
            except Course.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ Курс з ID {course_id} не знайдено')
                )
                return
        
        # Індексування всіх курсів
        queryset = Course.objects.all()
        if published_only:
            queryset = queryset.filter(is_published=True)
        
        courses = queryset.select_related('category').prefetch_related('tags', 'materials')
        total_courses = courses.count()
        
        if total_courses == 0:
            self.stdout.write(
                self.style.WARNING('Курси для індексування не знайдені')
            )
            return
        
        self.stdout.write(f'Індексування {total_courses} курсів...')
        
        indexed_count = 0
        failed_count = 0
        
        for course in courses:
            try:
                success = loader.index_course_content(course.id)
                if success:
                    indexed_count += 1
                    self.stdout.write(f'  ✅ {course.title}')
                else:
                    failed_count += 1
                    self.stdout.write(f'  ❌ {course.title}')
                    
            except Exception as e:
                failed_count += 1
                self.stdout.write(f'  ❌ {course.title}: {str(e)}')
        
        # Підсумок
        self.stdout.write('')
        self.stdout.write(f'📊 Результати індексування:')
        self.stdout.write(f'  - Успішно: {indexed_count}')
        self.stdout.write(f'  - Помилки: {failed_count}')
        self.stdout.write(f'  - Всього: {total_courses}')
        
        if indexed_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'✅ Індексування завершено!')
            )
        else:
            self.stdout.write(
                self.style.ERROR(f'❌ Жоден курс не було проіндексовано')
            )
