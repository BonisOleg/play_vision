"""
API Views for notifications app
"""
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import json
import logging

from .models import PushSubscription, Notification, NewsletterSubscriber

logger = logging.getLogger(__name__)


class VapidKeyView(View):
    """
    Отримання VAPID публічного ключа для push notifications
    """
    
    def get(self, request):
        """Повертає VAPID публічний ключ"""
        vapid_public_key = getattr(settings, 'VAPID_PUBLIC_KEY', '')
        
        if not vapid_public_key:
            # Якщо немає ключа, повертаємо дефолтний fallback
            logger.warning('VAPID_PUBLIC_KEY не налаштований, використовується дефолтний')
            vapid_public_key = 'BCm8_tLlWPYSlp4eFhPhGUo_lOxlJ-_Ps9LD2_tFQjDRGFIgDiMJtZGfHM0VkuT0xWMHCY8FZl3DfRMKRJ9r7V0'
        
        return JsonResponse({
            'publicKey': vapid_public_key
        })


@method_decorator(csrf_exempt, name='dispatch')
class PushSubscribeView(APIView):
    """
    Підписка користувача на push notifications
    """
    
    def post(self, request):
        """
        Створює підписку користувача на push notifications
        
        Expected JSON data:
        {
            "endpoint": "https://...",
            "p256dh": "...",
            "auth": "..."
        }
        """
        try:
            # Парсинг JSON даних
            data = json.loads(request.body.decode('utf-8'))
            
            # Якщо користувач не авторизований, створюємо анонімну підписку
            if not request.user.is_authenticated:
                return JsonResponse({
                    'success': False,
                    'error': 'Authentication required'
                }, status=403)
            
            # Валідація обов'язкових полів
            required_fields = ['endpoint', 'p256dh', 'auth']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }, status=400)
            
            # Отримання метаданих з User-Agent
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            browser = self._detect_browser(user_agent)
            device_type = self._detect_device_type(user_agent)
            
            # Створення або оновлення підписки
            subscription, created = PushSubscription.objects.update_or_create(
                user=request.user,
                endpoint=data['endpoint'],
                defaults={
                    'p256dh': data['p256dh'],
                    'auth': data['auth'],
                    'user_agent': user_agent,
                    'browser': browser,
                    'device_type': device_type,
                    'is_active': True,
                    'error_count': 0,
                    'last_error': '',
                }
            )
            
            logger.info(f'Push subscription {"created" if created else "updated"} for user {request.user.id}')
            
            return JsonResponse({
                'success': True,
                'message': 'Subscription saved successfully',
                'subscription_id': subscription.id
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f'Error creating push subscription: {str(e)}')
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)
    
    def _detect_browser(self, user_agent):
        """Визначає браузер з User-Agent"""
        user_agent = user_agent.lower()
        if 'chrome' in user_agent:
            return 'Chrome'
        elif 'firefox' in user_agent:
            return 'Firefox'
        elif 'safari' in user_agent and 'chrome' not in user_agent:
            return 'Safari'
        elif 'edge' in user_agent:
            return 'Edge'
        elif 'opera' in user_agent:
            return 'Opera'
        else:
            return 'Unknown'
    
    def _detect_device_type(self, user_agent):
        """Визначає тип пристрою з User-Agent"""
        user_agent = user_agent.lower()
        if any(mobile in user_agent for mobile in ['mobile', 'android', 'iphone']):
            return 'mobile'
        elif 'tablet' in user_agent or 'ipad' in user_agent:
            return 'tablet'
        else:
            return 'desktop'


@method_decorator(csrf_exempt, name='dispatch')  
class PushUnsubscribeView(APIView):
    """
    Скасування підписки на push notifications
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Скасовує підписку користувача"""
        try:
            data = json.loads(request.body.decode('utf-8'))
            
            if 'endpoint' not in data:
                return JsonResponse({
                    'success': False,
                    'error': 'Missing endpoint'
                }, status=400)
            
            # Знаходимо та деактивуємо підписку
            subscription = PushSubscription.objects.filter(
                user=request.user,
                endpoint=data['endpoint']
            ).first()
            
            if subscription:
                subscription.is_active = False
                subscription.save()
                
                logger.info(f'Push subscription deactivated for user {request.user.id}')
                
                return JsonResponse({
                    'success': True,
                    'message': 'Subscription removed successfully'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Subscription not found'
                }, status=404)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            logger.error(f'Error removing push subscription: {str(e)}')
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)


class NotificationListView(APIView):
    """
    Список сповіщень користувача
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Повертає список сповіщень користувача"""
        try:
            notifications = Notification.objects.filter(
                user=request.user
            ).order_by('-created_at')[:50]
            
            data = []
            for notification in notifications:
                data.append({
                    'id': notification.id,
                    'subject': notification.subject,
                    'content': notification.content,
                    'status': notification.status,
                    'created_at': notification.created_at.isoformat(),
                    'read_at': notification.read_at.isoformat() if notification.read_at else None,
                })
            
            return Response({
                'notifications': data,
                'count': len(data)
            })
            
        except Exception as e:
            logger.error(f'Error fetching notifications: {str(e)}')
            return Response({
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MarkAsReadView(APIView):
    """
    Позначити сповіщення як прочитане
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        """Позначає сповіщення як прочитане"""
        try:
            notification = Notification.objects.filter(
                id=pk,
                user=request.user
            ).first()
            
            if not notification:
                return Response({
                    'error': 'Notification not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            notification.mark_read()
            
            return Response({
                'success': True,
                'message': 'Notification marked as read'
            })
            
        except Exception as e:
            logger.error(f'Error marking notification as read: {str(e)}')
            return Response({
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class NewsletterSubscribeView(APIView):
    """
    Підписка на розсилку новин
    """
    
    def post(self, request):
        """
        Створює підписку на розсилку
        
        Expected JSON data:
        {
            "name": "Ім'я",
            "email": "email@example.com"
        }
        """
        try:
            # Отримання даних (DRF автоматично парсить JSON)
            data = request.data
            
            # Валідація обов'язкових полів
            name = data.get('name', '').strip()
            email = data.get('email', '').strip()
            
            if not name:
                return JsonResponse({
                    'success': False,
                    'error': 'Будь ласка, вкажіть ваше ім\'я'
                }, status=400)
            
            if not email:
                return JsonResponse({
                    'success': False,
                    'error': 'Будь ласка, вкажіть ваш email'
                }, status=400)
            
            # Базова валідація email
            if '@' not in email or '.' not in email:
                return JsonResponse({
                    'success': False,
                    'error': 'Будь ласка, вкажіть коректний email'
                }, status=400)
            
            # Отримання метаданих
            ip_address = self._get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Перевірка чи вже існує підписка
            existing_subscriber = NewsletterSubscriber.objects.filter(email=email).first()
            
            if existing_subscriber:
                if existing_subscriber.status == 'active':
                    return JsonResponse({
                        'success': False,
                        'error': 'Ви вже підписані на розсилку'
                    }, status=400)
                else:
                    # Якщо раніше відписався, повторно активуємо
                    existing_subscriber.status = 'active'
                    existing_subscriber.name = name
                    existing_subscriber.unsubscribed_at = None
                    existing_subscriber.save()
                    
                    logger.info(f'Newsletter resubscribed: {email}')
                    
                    return JsonResponse({
                        'success': True,
                        'message': 'Ви успішно підписалися на розсилку!'
                    })
            
            # Створення нового підписника
            subscriber = NewsletterSubscriber.objects.create(
                name=name,
                email=email,
                user=request.user if request.user.is_authenticated else None,
                source='footer_form',
                ip_address=ip_address,
                user_agent=user_agent,
                status='active'
            )
            
            logger.info(f'New newsletter subscriber: {email}')
            
            # TODO: Відправити welcome email
            # self._send_welcome_email(subscriber)
            
            return JsonResponse({
                'success': True,
                'message': 'Дякуємо за підписку! Ви будете отримувати наші новини.'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Невірний формат даних'
            }, status=400)
        except Exception as e:
            logger.error(f'Error creating newsletter subscription: {str(e)}')
            return JsonResponse({
                'success': False,
                'error': 'Виникла помилка. Спробуйте пізніше.'
            }, status=500)
    
    def _get_client_ip(self, request):
        """Отримує IP адресу клієнта"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip