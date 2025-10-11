from django.core.management.base import BaseCommand
from apps.content.models import Tag


class Command(BaseCommand):
    help = 'Створити Interest tags для cabinet'
    
    def handle(self, *args, **options):
        interests = [
            ('training', 'тренерство', 1),
            ('analytics', 'аналітика і скаутинг', 2),
            ('fitness', 'ЗФП', 3),
            ('management', 'менеджмент', 4),
            ('psychology', 'психологія', 5),
            ('nutrition', 'нутриціологія', 6),
            ('player', 'футболіст', 7),
            ('parent', 'батько', 8),
        ]
        
        created_count = 0
        updated_count = 0
        
        for slug, name, order in interests:
            tag, created = Tag.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'tag_type': 'interest',
                    'display_order': order
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✅ Створено: {name}'))
            else:
                # Оновити існуючий тег
                if tag.tag_type != 'interest' or tag.display_order != order:
                    tag.tag_type = 'interest'
                    tag.name = name
                    tag.display_order = order
                    tag.save()
                    updated_count += 1
                    self.stdout.write(self.style.WARNING(f'🔄 Оновлено: {name}'))
                else:
                    self.stdout.write(f'  Вже існує: {name}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Готово! Створено: {created_count}, Оновлено: {updated_count}'
            )
        )

