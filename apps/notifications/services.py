"""
Push Notification Service для PWA Play Vision
Реалізація згідно MainPlan.mdc
"""
import json
import logging
from django.conf import settings
from django.utils import timezone
from .models import PushSubscription, Notification

logger = logging.getLogger(__name__)


class PushNotificationService:
    """
    Сервіс push-сповіщень з підтримкою iOS PWA (згідно MainPlan.mdc)
    """
    
    def __init__(self):
        self.vapid_private_key = getattr(settings, 'VAPID_PRIVATE_KEY', '')
        self.vapid_public_key = getattr(settings, 'VAPID_PUBLIC_KEY', '')
        self.vapid_email = getattr(settings, 'VAPID_EMAIL', settings.DEFAULT_FROM_EMAIL)
    
    def setup_vapid(self):
        """Налаштування VAPID ключів (згідно MainPlan.mdc)"""
        if not self.vapid_private_key or not self.vapid_public_key:
            try:
                from pywebpush import generate_vapid_keys
                
                vapid_keys = generate_vapid_keys()
                
                print("VAPID Keys generated! Add to your settings:")
                print(f"VAPID_PRIVATE_KEY = '{vapid_keys['private_key']}'")
                print(f"VAPID_PUBLIC_KEY = '{vapid_keys['public_key']}'")
                
                return vapid_keys
                
            except ImportError:
                logger.error("pywebpush not installed. Run: pip install pywebpush")
                return None
        
        return {
            'private_key': self.vapid_private_key,
            'public_key': self.vapid_public_key
        }
    
    def subscribe_user(self, user, subscription_info):
        """Підписка користувача на push (згідно MainPlan.mdc)"""
        push_subscription, created = PushSubscription.objects.update_or_create(
            user=user,
            endpoint=subscription_info['endpoint'],
            defaults={
                'p256dh': subscription_info['keys']['p256dh'],
                'auth': subscription_info['keys']['auth'],
                'is_active': True
            }
        )
        
        return push_subscription, created
    
    def send_push_to_user(self, user, title, body, data=None):
        """Відправка push-сповіщення користувачу"""
        subscriptions = PushSubscription.objects.filter(
            user=user,
            is_active=True
        )
        
        sent_count = 0
        for subscription in subscriptions:
            try:
                success = self.send_push_to_subscription(subscription, {
                    'title': title,
                    'body': body,
                    'data': data or {}
                })
                if success:
                    sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send push to subscription {subscription.id}: {e}")
        
        return sent_count
    
    def send_push_to_subscription(self, subscription, message_data):
        """Відправка push до конкретної підписки"""
        if not self.vapid_private_key:
            logger.warning("VAPID keys not configured, using mock mode")
            return self._mock_push_send(subscription, message_data)
        
        try:
            from pywebpush import webpush, WebPushException
            
            subscription_info = {
                'endpoint': subscription.endpoint,
                'keys': {
                    'p256dh': subscription.p256dh,
                    'auth': subscription.auth
                }
            }
            
            payload = json.dumps({
                'title': message_data['title'],
                'body': message_data['body'],
                'icon': '/static/icons/icon-192x192.png',
                'badge': '/static/icons/badge-72x72.png',
                'data': message_data.get('data', {}),
                'actions': [
                    {'action': 'open', 'title': 'Відкрити'},
                    {'action': 'close', 'title': 'Закрити'}
                ],
                'requireInteraction': message_data.get('requireInteraction', False),
                'tag': message_data.get('tag', 'playvision-notification')
            })
            
            response = webpush(
                subscription_info=subscription_info,
                data=payload,
                vapid_private_key=self.vapid_private_key,
                vapid_claims={
                    'sub': f'mailto:{self.vapid_email}'
                }
            )
            
            # Оновити статистику підписки
            subscription.messages_sent += 1
            subscription.last_sent_at = timezone.now()
            subscription.save()
            
            logger.info(f"Push sent successfully to subscription {subscription.id}")
            return True
            
        except ImportError:
            logger.error("pywebpush not installed. Using mock mode.")
            return self._mock_push_send(subscription, message_data)
            
        except Exception as e:
            # Деактивувати невалідні підписки (410 Gone)
            if hasattr(e, 'response') and e.response.status_code == 410:
                subscription.is_active = False
                subscription.save()
                logger.info(f"Deactivated invalid subscription {subscription.id}")
            else:
                logger.error(f"Push notification failed: {e}")
            
            return False
    
    def _mock_push_send(self, subscription, message_data):
        """Mock відправка для тестування без реальних push"""
        print(f"[MOCK PUSH] To: {subscription.endpoint[:50]}...")
        print(f"[MOCK PUSH] Title: {message_data['title']}")
        print(f"[MOCK PUSH] Body: {message_data['body']}")
        
        # Оновити статистику
        subscription.messages_sent += 1
        subscription.last_sent_at = timezone.now()
        subscription.save()
        
        return True
    
    def send_course_notification(self, course, users=None):
        """Відправка повідомлення про новий курс"""
        if not users:
            # Всім підписникам
            users = PushSubscription.objects.filter(
                is_active=True,
                user__isnull=False
            ).values_list('user', flat=True).distinct()
        
        sent_count = 0
        for user_id in users:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(id=user_id)
                
                success_count = self.send_push_to_user(
                    user=user,
                    title='🎓 Новий курс на Play Vision!',
                    body=f'Доступний курс "{course.title}" від провідних експертів',
                    data={
                        'url': f'/hub/course/{course.slug}/',
                        'course_id': course.id,
                        'action_type': 'new_course'
                    }
                )
                sent_count += success_count
                
            except Exception as e:
                logger.error(f"Failed to send course notification to user {user_id}: {e}")
        
        logger.info(f"Course notification sent to {sent_count} users")
        return sent_count
    
    def send_subscription_reminder(self, user, days_until_expiry):
        """Нагадування про закінчення підписки"""
        if days_until_expiry <= 3:
            urgency = 'високий'
            emoji = '🚨'
        elif days_until_expiry <= 7:
            urgency = 'середній'
            emoji = '⏰'
        else:
            urgency = 'низький'
            emoji = '📅'
        
        sent_count = self.send_push_to_user(
            user=user,
            title=f'{emoji} Підписка закінчується',
            body=f'Ваша підписка Play Vision закінчується через {days_until_expiry} днів',
            data={
                'url': '/account/subscription/',
                'urgency': urgency,
                'days_until_expiry': days_until_expiry,
                'action_type': 'subscription_reminder'
            }
        )
        
        return sent_count > 0
    
    def send_ai_tip_of_day(self, user, tip_content):
        """Щоденна порада від AI"""
        sent_count = self.send_push_to_user(
            user=user,
            title='💡 Порада дня від AI',
            body=tip_content[:100] + '...' if len(tip_content) > 100 else tip_content,
            data={
                'url': '/ai/chat/',
                'tip_content': tip_content,
                'action_type': 'daily_tip'
            }
        )
        
        return sent_count > 0
    
    def get_push_stats(self):
        """Статистика push повідомлень"""
        total_subscriptions = PushSubscription.objects.count()
        active_subscriptions = PushSubscription.objects.filter(is_active=True).count()
        
        # Статистика за останні 30 днів
        from django.utils import timezone
        from datetime import timedelta
        
        last_30_days = timezone.now() - timedelta(days=30)
        recent_notifications = Notification.objects.filter(
            created_at__gte=last_30_days,
            template__notification_type='push'
        )
        
        stats = {
            'total_subscriptions': total_subscriptions,
            'active_subscriptions': active_subscriptions,
            'inactive_subscriptions': total_subscriptions - active_subscriptions,
            'notifications_sent_30d': recent_notifications.filter(status='sent').count(),
            'notifications_delivered_30d': recent_notifications.filter(status='delivered').count(),
            'delivery_rate': 0
        }
        
        if stats['notifications_sent_30d'] > 0:
            stats['delivery_rate'] = round(
                (stats['notifications_delivered_30d'] / stats['notifications_sent_30d']) * 100, 
                2
            )
        
        return stats
