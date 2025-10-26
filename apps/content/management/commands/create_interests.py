"""
Management command to create default user interests
"""
from django.core.management.base import BaseCommand
from apps.content.models import Tag


class Command(BaseCommand):
    help = 'Створює початкові теги-інтереси користувачів'

    def handle(self, *args, **options):
        interests = [
            ('Футбол', 'football', 1),
            ('Баскетбол', 'basketball', 2),
            ('Волейбол', 'volleyball', 3),
            ('Теніс', 'tennis', 4),
            ('Хокей', 'hockey', 5),
            ('Гандбол', 'handball', 6),
            ('Психологія спорту', 'psychology', 7),
            ('Спортивна аналітика', 'analytics', 8),
            ('Тренування', 'training', 9),
            ('Харчування', 'nutrition', 10),
            ('Реабілітація', 'rehabilitation', 11),
            ('Фізична підготовка', 'fitness', 12),
            ('Тактика', 'tactics', 13),
            ('Менеджмент', 'management', 14),
            ('Мотивація', 'motivation', 15),
        ]

        created_count = 0
        updated_count = 0

        for name, slug, order in interests:
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
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Створено інтерес: {name}')
                )
            else:
                # Update existing
                tag.name = name
                tag.tag_type = 'interest'
                tag.display_order = order
                tag.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'⟳ Оновлено інтерес: {name}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Завершено! Створено: {created_count}, Оновлено: {updated_count}'
            )
        )
