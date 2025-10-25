"""
Management command для автоматичного продовження підписок
Запускати щодня через cron або планувальник задач
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.subscriptions.models import Subscription, Plan
from apps.payments.liqpay_service import LiqPayService


class Command(BaseCommand):
    help = 'Автоматично продовжує підписки, термін яких закінчується'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days-before',
            type=int,
            default=3,
            help='За скільки днів до закінчення почати продовження (за замовчуванням: 3)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Тестовий режим - не виконувати реальні списання'
        )

    def handle(self, *args, **options):
        days_before = options['days_before']
        dry_run = options['dry_run']
        
        # Знаходимо підписки, які скоро закінчуються
        renewal_date = timezone.now() + timedelta(days=days_before)
        
        subscriptions_to_renew = Subscription.objects.filter(
            status='active',
            auto_renew=True,
            end_date__lte=renewal_date,
            end_date__gte=timezone.now()
        )
        
        self.stdout.write(
            self.style.NOTICE(
                f'Знайдено {subscriptions_to_renew.count()} підписок для продовження'
            )
        )
        
        if dry_run:
            self.stdout.write(self.style.WARNING('=== ТЕСТОВИЙ РЕЖИМ ==='))
        
        renewed_count = 0
        failed_count = 0
        
        for subscription in subscriptions_to_renew:
            try:
                if dry_run:
                    self.stdout.write(
                        f'[DRY RUN] Підписка {subscription.id} для {subscription.user.email} '
                        f'буде продовжена на {subscription.plan.duration_months} міс.'
                    )
                    renewed_count += 1
                else:
                    self._renew_subscription(subscription)
                    renewed_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Продовжено підписку {subscription.id} для {subscription.user.email}'
                        )
                    )
            except Exception as e:
                failed_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Помилка продовження підписки {subscription.id}: {str(e)}'
                    )
                )
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Успішно: {renewed_count}'))
        if failed_count > 0:
            self.stdout.write(self.style.ERROR(f'Помилки: {failed_count}'))
    
    def _renew_subscription(self, subscription):
        """
        Продовжує підписку через LiqPay рекурентний платіж
        """
        # LiqPay автоматично списує кошти для підписок
        # Тут просто оновлюємо дати
        subscription.end_date = subscription.end_date + timedelta(
            days=30 * subscription.plan.duration_months
        )
        subscription.save()
        
        # Інкрементуємо лічильник підписок для статистики
        subscription.plan.total_subscriptions += 1
        subscription.plan.save()
        
        # Можна додати логіку відправки повідомлення користувачу
        self._notify_user(subscription)
    
    def _notify_user(self, subscription):
        """Відправляє повідомлення користувачу про продовження"""
        try:
            from apps.notifications.services import NotificationService
            notification_service = NotificationService()
            notification_service.send_subscription_renewed(
                user=subscription.user,
                subscription=subscription
            )
        except Exception:
            pass  # Notifications необов'язкові

