from django.core.management.base import BaseCommand
from apps.content.models import Tag


class Command(BaseCommand):
    help = 'Створює стандартні інтереси для користувачів у фіксованій послідовності'

    def handle(self, *args, **kwargs):
        interests_data = [
            (1, 'Тренерство'),
            (2, 'Аналітика і скаутинг'),
            (3, 'ЗФП'),
            (4, 'Менеджмент'),
            (5, 'Психологія'),
            (6, 'Нутриціологія'),
            (7, 'Футболіст'),
            (8, 'Батько'),
            (9, 'Реабілітація'),
        ]
        
        self.stdout.write('Створення стандартних інтересів...')
        
        for order, name in interests_data:
            slug = name.lower().replace(' ', '-').replace('і', 'i')
            
            tag, created = Tag.objects.update_or_create(
                name=name,
                tag_type='interest',
                defaults={
                    'slug': slug,
                    'display_order': order
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Створено: {name} (порядок: {order})'))
            else:
                self.stdout.write(f'  Оновлено: {name} (порядок: {order})')
        
        self.stdout.write(self.style.SUCCESS('\n✓ Всі інтереси успішно створено!'))
        self.stdout.write(f'Всього створено: {len(interests_data)} інтересів')
