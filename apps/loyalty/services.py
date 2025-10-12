from typing import Optional, Tuple
from decimal import Decimal
from django.contrib.auth import get_user_model
from .models import LoyaltyAccount, PointEarningRule, RedemptionOption

User = get_user_model()


class LoyaltyService:
    """
    Сервіс для роботи з програмою лояльності
    """

    @staticmethod
    def get_or_create_account(user: User) -> LoyaltyAccount:
        """Отримати або створити аккаунт лояльності"""
        account, created = LoyaltyAccount.objects.get_or_create(user=user)
        return account

    @staticmethod
    def get_user_subscription_tier(user: User) -> str:
        """
        Визначити рівень підписки користувача
        Повертає: 'none', 'c_vision', 'b_vision', 'a_vision', 'pro_vision'
        """
        if not user.is_authenticated:
            return 'none'

        # Перевірити активну підписку
        try:
            subscription = user.subscriptions.filter(status='active').first()
            if not subscription:
                return 'none'

            plan_name = subscription.plan.slug.lower()

            if 'pro' in plan_name or 'pro-vision' in plan_name:
                return 'pro_vision'
            elif 'a-vision' in plan_name or plan_name.startswith('a_'):
                return 'a_vision'
            elif 'b-vision' in plan_name or plan_name.startswith('b_'):
                return 'b_vision'
            elif 'c-vision' in plan_name or plan_name.startswith('c_'):
                return 'c_vision'

            return 'none'
        except Exception:
            return 'none'

    @classmethod
    def award_points_for_purchase(cls, user: User, amount: Decimal, order_id: int) -> int:
        """
        Нарахувати бали за покупку згідно матриці
        """
        if amount <= 0:
            return 0

        account = cls.get_or_create_account(user)
        tier = cls.get_user_subscription_tier(user)

        points = PointEarningRule.get_points_for_purchase(amount, tier)

        if points > 0:
            account.add_points(
                points=points,
                transaction_type='purchase',
                reason=f'Покупка на суму ₴{amount}',
                reference_type='order',
                reference_id=order_id
            )

        return points

    @classmethod
    def award_points_for_subscription(cls, user: User, subscription_tier: str,
                                      duration_months: int, subscription_id: int) -> int:
        """
        Нарахувати бали за оформлення підписки
        """
        account = cls.get_or_create_account(user)

        # Нормалізувати tier
        tier_map = {
            'c-vision': 'c_vision',
            'b-vision': 'b_vision',
            'a-vision': 'a_vision',
            'pro-vision': 'pro_vision',
        }
        normalized_tier = tier_map.get(subscription_tier.lower(), subscription_tier.lower())

        points = PointEarningRule.get_points_for_subscription(normalized_tier, duration_months)

        if points > 0:
            account.add_points(
                points=points,
                transaction_type='subscription',
                reason=f'Підписка {subscription_tier} на {duration_months} міс',
                reference_type='subscription',
                reference_id=subscription_id
            )

        return points

    @classmethod
    def calculate_discount_from_points(cls, user: User, subtotal: Decimal) -> Tuple[int, Decimal]:
        """
        Розрахувати знижку на основі балів
        Повертає: (відсоток_знижки, сума_знижки)
        """
        if subtotal <= 0:
            return 0, Decimal('0')

        account = cls.get_or_create_account(user)
        discount_percentage = account.get_discount_percentage()

        if discount_percentage == 0:
            return 0, Decimal('0')

        discount_amount = subtotal * Decimal(discount_percentage) / Decimal('100')
        return discount_percentage, discount_amount

    @classmethod
    def apply_discount_for_points(cls, user: User, discount_percentage: int,
                                  discount_amount: Decimal, order_id: int) -> bool:
        """
        Списати бали за використання знижки
        """
        account = cls.get_or_create_account(user)

        points_to_spend = 0
        if discount_percentage == 5:
            points_to_spend = 50
        elif discount_percentage == 10:
            points_to_spend = 100
        else:
            return False

        success = account.spend_points(
            points=points_to_spend,
            reason=f'Знижка {discount_percentage}% (₴{discount_amount})',
            reference_type='order',
            reference_id=order_id
        )

        return success

    @classmethod
    def get_points_for_course_display(cls, course_price: Decimal, user: Optional[User] = None) -> int:
        """
        Отримати кількість балів для відображення на картці курсу
        """
        if not user or not user.is_authenticated:
            tier = 'none'
        else:
            tier = cls.get_user_subscription_tier(user)

        return PointEarningRule.get_points_for_purchase(course_price, tier)

    @classmethod
    def can_redeem_subscription_month(cls, user: User, tier: str = 'c_vision') -> Tuple[bool, int]:
        """
        Перевірити чи користувач може обміняти бали на місяць підписки
        Повертає: (можливо, потрібно_балів)
        """
        account = cls.get_or_create_account(user)

        # Знайти опцію обміну
        option = RedemptionOption.objects.filter(
            option_type='subscription_month',
            subscription_tier=tier,
            is_active=True
        ).first()

        if not option:
            return False, 0

        has_subscription = cls.get_user_subscription_tier(user) != 'none'
        can_redeem = option.can_redeem(account.points, has_subscription)

        return can_redeem, option.points_required

    @classmethod
    def redeem_subscription_month(cls, user: User, tier: str, subscription_id: int) -> bool:
        """
        Обміняти бали на місяць підписки (200-500 балів)
        """
        account = cls.get_or_create_account(user)

        option = RedemptionOption.objects.filter(
            option_type='subscription_month',
            subscription_tier=tier,
            is_active=True
        ).first()

        if not option:
            return False

        has_subscription = cls.get_user_subscription_tier(user) != 'none'
        if not option.can_redeem(account.points, has_subscription):
            return False

        success = account.spend_points(
            points=option.points_required,
            reason=f'Обмін на місяць {tier.upper()}',
            reference_type='subscription',
            reference_id=subscription_id
        )

        return success

    @classmethod
    def get_available_redemption_options(cls, user: User) -> list:
        """
        Отримати доступні опції витрати балів
        """
        account = cls.get_or_create_account(user)
        has_subscription = cls.get_user_subscription_tier(user) != 'none'

        options = RedemptionOption.objects.filter(is_active=True)

        available = []
        for option in options:
            if option.can_redeem(account.points, has_subscription):
                available.append({
                    'id': option.id,
                    'name': option.name,
                    'points_required': option.points_required,
                    'type': option.option_type,
                    'description': option.description,
                    'can_afford': True
                })
            elif not option.requires_subscription or has_subscription:
                available.append({
                    'id': option.id,
                    'name': option.name,
                    'points_required': option.points_required,
                    'type': option.option_type,
                    'description': option.description,
                    'can_afford': False
                })

        return available

