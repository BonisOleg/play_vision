from django.core.management.base import BaseCommand
from apps.loyalty.models import PointEarningRule, RedemptionOption
from decimal import Decimal


class Command(BaseCommand):
    help = 'Ініціалізація правил програми лояльності згідно скрінів'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🎯 Ініціалізація правил програми лояльності...'))

        # Очистити старі правила
        PointEarningRule.objects.all().delete()
        RedemptionOption.objects.all().delete()

        # === ПРАВИЛА НАРАХУВАННЯ ЗА ПОКУПКИ ===
        purchase_rules = [
            # Без підписки
            {'tier': 'none', 'min': 399, 'max': 1000, 'points': 5},
            {'tier': 'none', 'min': 1000, 'max': 3000, 'points': 10},
            {'tier': 'none', 'min': 3000, 'max': None, 'points': 15},

            # C-Vision / B-Vision
            {'tier': 'c_vision', 'min': 399, 'max': 1000, 'points': 8},
            {'tier': 'c_vision', 'min': 1000, 'max': 3000, 'points': 15},
            {'tier': 'c_vision', 'min': 3000, 'max': None, 'points': 23},

            {'tier': 'b_vision', 'min': 399, 'max': 1000, 'points': 8},
            {'tier': 'b_vision', 'min': 1000, 'max': 3000, 'points': 15},
            {'tier': 'b_vision', 'min': 3000, 'max': None, 'points': 23},

            # A-Vision / Pro-Vision
            {'tier': 'a_vision', 'min': 399, 'max': 1000, 'points': 10},
            {'tier': 'a_vision', 'min': 1000, 'max': 3000, 'points': 20},
            {'tier': 'a_vision', 'min': 3000, 'max': None, 'points': 30},

            {'tier': 'pro_vision', 'min': 399, 'max': 1000, 'points': 10},
            {'tier': 'pro_vision', 'min': 1000, 'max': 3000, 'points': 20},
            {'tier': 'pro_vision', 'min': 3000, 'max': None, 'points': 30},
        ]

        order = 0
        for rule in purchase_rules:
            PointEarningRule.objects.create(
                rule_type='purchase',
                subscription_tier=rule['tier'],
                min_amount=Decimal(str(rule['min'])),
                max_amount=Decimal(str(rule['max'])) if rule['max'] else None,
                points=rule['points'],
                is_active=True,
                order=order
            )
            order += 1

        # === ПРАВИЛА НАРАХУВАННЯ ЗА ПІДПИСКИ ===
        subscription_rules = [
            # C-Vision / B-Vision
            {'tier': 'c_vision', 'months': 1, 'points': 15},
            {'tier': 'c_vision', 'months': 3, 'points': 50},
            {'tier': 'c_vision', 'months': 6, 'points': 100},
            {'tier': 'c_vision', 'months': 12, 'points': 200},

            {'tier': 'b_vision', 'months': 1, 'points': 15},
            {'tier': 'b_vision', 'months': 3, 'points': 50},
            {'tier': 'b_vision', 'months': 6, 'points': 100},
            {'tier': 'b_vision', 'months': 12, 'points': 200},

            # A-Vision / Pro-Vision
            {'tier': 'a_vision', 'months': 3, 'points': 80},
            {'tier': 'a_vision', 'months': 6, 'points': 160},
            {'tier': 'a_vision', 'months': 12, 'points': 320},

            {'tier': 'pro_vision', 'months': 3, 'points': 80},
            {'tier': 'pro_vision', 'months': 6, 'points': 160},
            {'tier': 'pro_vision', 'months': 12, 'points': 320},
        ]

        for rule in subscription_rules:
            PointEarningRule.objects.create(
                rule_type='subscription',
                subscription_tier=rule['tier'],
                subscription_duration_months=rule['months'],
                points=rule['points'],
                is_active=True,
                order=order
            )
            order += 1

        # === ПРАВИЛА ВИТРАТ ===
        # Знижки (без підписки)
        RedemptionOption.objects.create(
            option_type='discount',
            name='Знижка 5%',
            description='Знижка 5% на наступну покупку',
            points_required=50,
            discount_percentage=5,
            requires_subscription=False,
            is_active=True,
            display_order=1
        )

        RedemptionOption.objects.create(
            option_type='discount',
            name='Знижка 10%',
            description='Знижка 10% на наступну покупку',
            points_required=100,
            discount_percentage=10,
            requires_subscription=False,
            is_active=True,
            display_order=2
        )

        # Обмін на місяць підписки (тільки C/B-Vision)
        RedemptionOption.objects.create(
            option_type='subscription_month',
            name='Місяць C-Vision',
            description='Обмін балів на повний місяць C-Vision підписки',
            points_required=200,
            subscription_tier='c_vision',
            requires_subscription=True,
            is_active=True,
            display_order=3
        )

        RedemptionOption.objects.create(
            option_type='subscription_month',
            name='Місяць B-Vision',
            description='Обмін балів на повний місяць B-Vision підписки',
            points_required=350,
            subscription_tier='b_vision',
            requires_subscription=True,
            is_active=True,
            display_order=4
        )

        self.stdout.write(self.style.SUCCESS(f'✅ Створено {PointEarningRule.objects.count()} правил нарахування'))
        self.stdout.write(self.style.SUCCESS(f'✅ Створено {RedemptionOption.objects.count()} опцій витрати'))
        self.stdout.write(self.style.SUCCESS('🎉 Ініціалізація завершена!'))

