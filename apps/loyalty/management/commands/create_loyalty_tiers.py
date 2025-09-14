from django.core.management.base import BaseCommand
from apps.loyalty.models import LoyaltyTier


class Command(BaseCommand):
    help = 'Create initial loyalty tiers'

    def handle(self, *args, **options):
        tiers_data = [
            {
                'name': 'Bronze',
                'points_required': 0,
                'discount_percentage': 0,
                'color': '#cd7f32',
                'benefits': ['Базовий доступ до контенту'],
                'order': 1
            },
            {
                'name': 'Silver',
                'points_required': 200,
                'discount_percentage': 5,
                'color': '#c0c0c0',
                'benefits': ['5% знижка на матеріали', 'Пріоритетна підтримка'],
                'order': 2
            },
            {
                'name': 'Gold',
                'points_required': 500,
                'discount_percentage': 10,
                'color': '#ffd700',
                'benefits': ['10% знижка на матеріали', 'Ексклюзивні вебінари', 'Персональні рекомендації'],
                'order': 3
            },
            {
                'name': 'Platinum',
                'points_required': 1000,
                'discount_percentage': 15,
                'color': '#e5e4e2',
                'benefits': ['15% знижка на матеріали', 'VIP доступ до івентів', 'Персональний менеджер', 'Ранній доступ до новинок'],
                'order': 4
            }
        ]

        for tier_data in tiers_data:
            tier, created = LoyaltyTier.objects.get_or_create(
                name=tier_data['name'],
                defaults=tier_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Створено рівень: {tier.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Рівень вже існує: {tier.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('Успішно створено всі рівні лояльності!')
        )
