"""
API Views для Push Notifications PWA
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.conf import settings
import json
from .models import PushSubscription, Notification


class PushSubscribeAPIView(APIView):
    """Підписка на push notifications"""
    
    def post(self, request):
        try:
            data = request.data
            subscription_info = data.get('subscription')
            
            if not subscription_info:
                return Response(
                    {'error': 'Subscription info required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Створити або оновити підписку
            push_subscription, created = PushSubscription.objects.update_or_create(
                user=request.user if request.user.is_authenticated else None,
                endpoint=subscription_info['endpoint'],
                defaults={
                    'p256dh': subscription_info['keys']['p256dh'],
                    'auth': subscription_info['keys']['auth'],
                    'is_active': True,
                    'browser_info': request.META.get('HTTP_USER_AGENT', '')[:200]
                }
            )
            
            message = 'Підписка створена' if created else 'Підписка оновлена'
            
            return Response({
                'success': True,
                'message': message,
                'subscription_id': push_subscription.id
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PushUnsubscribeAPIView(APIView):
    """Відписка від push notifications"""
    
    def post(self, request):
        try:
            subscription_id = request.data.get('subscription_id')
            
            if subscription_id:
                PushSubscription.objects.filter(
                    id=subscription_id,
                    user=request.user if request.user.is_authenticated else None
                ).update(is_active=False)
            else:
                # Деактивувати всі підписки користувача
                PushSubscription.objects.filter(
                    user=request.user if request.user.is_authenticated else None
                ).update(is_active=False)
            
            return Response({
                'success': True,
                'message': 'Підписку скасовано'
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PushTestAPIView(APIView):
    """Тестове push повідомлення (тільки для staff)"""
    
    def post(self, request):
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            from .services import PushNotificationService
            
            service = PushNotificationService()
            
            # Відправити тестове повідомлення всім активним підпискам
            test_data = {
                'title': 'Тест Play Vision',
                'body': 'Це тестове push повідомлення з Play Vision PWA',
                'icon': '/static/icons/icon-192x192.png',
                'badge': '/static/icons/badge-72x72.png',
                'data': {
                    'url': '/',
                    'test': True
                }
            }
            
            active_subscriptions = PushSubscription.objects.filter(is_active=True)
            sent_count = 0
            
            for subscription in active_subscriptions:
                try:
                    success = service.send_push_to_subscription(subscription, test_data)
                    if success:
                        sent_count += 1
                except Exception as e:
                    print(f"Failed to send to subscription {subscription.id}: {e}")
            
            return Response({
                'success': True,
                'message': f'Відправлено {sent_count} тестових повідомлень',
                'sent_count': sent_count,
                'total_subscriptions': active_subscriptions.count()
            })
            
        except ImportError:
            return Response(
                {'error': 'Push notification service not configured'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class NotificationHistoryAPIView(APIView):
    """Історія повідомлень користувача"""
    
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')[:20]
        
        data = []
        for notification in notifications:
            data.append({
                'id': notification.id,
                'subject': notification.subject,
                'content': notification.content[:100] + '...' if len(notification.content) > 100 else notification.content,
                'status': notification.status,
                'created_at': notification.created_at.isoformat(),
                'sent_at': notification.sent_at.isoformat() if notification.sent_at else None,
                'read_at': notification.read_at.isoformat() if notification.read_at else None
            })
        
        return Response({
            'notifications': data,
            'total': notifications.count()
        })
