from django.core.management.base import BaseCommand
from apps.content.models import Tag, Category


class Command(BaseCommand):
    help = 'Створити теги інтересів та категорії згідно usertask.md'

    def handle(self, *args, **options):
        self.stdout.write('Створюємо інтереси...')
        
        # Інтереси для профілю користувача (чітка послідовність)
        interests_data = [
            ('Тренерство', 1),
            ('Аналітика і скаутинг', 2),
            ('ЗФП', 3),
            ('Менеджмент', 4),
            ('Психологія', 5),
            ('Нутриціологія', 6),  # НЕ "харчування"!
            ('Футболіст', 7),
            ('Батько', 8),
            ('Реабілітація', 9),
        ]
        
        for name, order in interests_data:
            tag, created = Tag.objects.get_or_create(
                name=name,
                tag_type='interest',
                defaults={
                    'display_order': order,
                    'slug': name.lower().replace(' ', '-').replace('і', 'i'),
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Створено інтерес: {name}'))
            else:
                # Оновити display_order якщо інтерес вже існує
                tag.display_order = order
                tag.save()
                self.stdout.write(f'  Інтерес вже існує (оновлено порядок): {name}')
        
        self.stdout.write('')
        self.stdout.write('Створюємо категорії курсів...')
        
        # Категорії для фільтрації курсів
        categories_data = [
            ('Тренерство', 1, [
                'Тренер воротарів',
                'Дитячий тренер',
                'Тренер ЗФП',
                'Тренер професійних команд',
            ]),
            ('Аналітика і скаутинг', 2, []),
            ('Менеджмент', 3, []),
            ('Спортивна психологія', 4, []),
            ('Нутриціологія', 5, []),
            ('Реабілітація', 6, []),
            ('Футболіст', 7, []),
            ('Батько', 8, []),
        ]
        
        for name, order, subcats in categories_data:
            cat, created = Category.objects.get_or_create(
                name=name,
                defaults={
                    'display_order': order,
                    'slug': name.lower().replace(' ', '-').replace('і', 'i'),
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Створено категорію: {name}'))
            else:
                # Оновити display_order
                cat.display_order = order
                cat.is_active = True
                cat.save()
                self.stdout.write(f'  Категорія вже існує (оновлено): {name}')
            
            # Підкатегорії
            for idx, sub_name in enumerate(subcats, start=1):
                sub_cat, sub_created = Category.objects.get_or_create(
                    name=sub_name,
                    parent=cat,
                    defaults={
                        'slug': sub_name.lower().replace(' ', '-'),
                        'display_order': idx,
                        'is_active': True,
                    }
                )
                if sub_created:
                    self.stdout.write(f'  ✓ Створено підкатегорію: {sub_name}')
                else:
                    sub_cat.display_order = idx
                    sub_cat.is_active = True
                    sub_cat.save()
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ Всі інтереси та категорії створено!'))
        self.stdout.write('')
        self.stdout.write('Підсумок:')
        self.stdout.write(f'  • Інтересів: {Tag.objects.filter(tag_type="interest").count()}')
        self.stdout.write(f'  • Категорій: {Category.objects.filter(parent__isnull=True).count()}')
        self.stdout.write(f'  • Підкатегорій: {Category.objects.filter(parent__isnull=False).count()}')
