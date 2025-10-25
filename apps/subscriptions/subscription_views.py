"""
Views для оформлення підписки
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.conf import settings
from django.db import models

from .models import Plan, Subscription
from apps.payments.liqpay_service import LiqPayService
from apps.payments.models import Coupon


class SubscriptionCheckoutView(LoginRequiredMixin, TemplateView):
    """
    Окрема сторінка оформлення підписки
    """
    template_name = 'subscriptions/checkout.html'
    login_url = '/auth/login/'
    
    def get_login_url(self):
        """Зберігаємо вибраний план при редіректі"""
        login_url = super().get_login_url()
        plan_id = self.kwargs.get('plan_id')
        if plan_id:
            return f"{login_url}?next={self.request.path}&plan_id={plan_id}"
        return login_url
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        plan_id = kwargs.get('plan_id')
        
        # Отримуємо план
        plan = get_object_or_404(Plan, id=plan_id, is_active=True)
        context['plan'] = plan
        context['user'] = self.request.user
        
        # Перевіряємо чи є вже активна підписка
        active_subscription = self.request.user.subscriptions.filter(
            status='active'
        ).first()
        context['has_active_subscription'] = active_subscription is not None
        context['active_subscription'] = active_subscription
        
        # Розраховуємо порівняння з окремими покупками
        context['comparison_data'] = self._calculate_purchase_comparison()
        
        # Способи оплати
        context['payment_methods'] = [
            {'id': 'card', 'name': 'Картка Visa/Mastercard', 'icon': 'card'},
            {'id': 'apple_pay', 'name': 'Apple Pay', 'icon': 'apple'},
            {'id': 'google_pay', 'name': 'Google Pay', 'icon': 'google'},
            {'id': 'privat24', 'name': 'Приват24', 'icon': 'privat'},
        ]
        
        # Інформація про автопродовження
        context['auto_renew_info'] = {
            'enabled': True,
            'text': 'Підписка продовжується автоматично. Ви можете скасувати у будь-який момент.',
            'next_payment_date': self._calculate_next_payment_date(plan)
        }
        
        return context
    
    def _calculate_purchase_comparison(self):
        """
        Розраховує скільки користувач вже витратив на окремі покупки
        та порівнює з вартістю підписки
        """
        user = self.request.user
        
        # Підраховуємо всі покупки курсів
        from apps.payments.models import Order
        
        total_spent = Order.objects.filter(
            user=user,
            status='completed',
            items__item_type='course'
        ).aggregate(total=models.Sum('total'))['total'] or 0
        
        # Підраховуємо кількість куплених курсів
        purchased_courses_count = Order.objects.filter(
            user=user,
            status='completed',
            items__item_type='course'
        ).distinct().count()
        
        return {
            'total_spent': total_spent,
            'courses_count': purchased_courses_count,
            'has_purchases': total_spent > 0
        }
    
    def _calculate_next_payment_date(self, plan):
        """Розраховує дату наступного платежу"""
        from django.utils import timezone
        from datetime import timedelta
        
        return timezone.now() + timedelta(days=30 * plan.duration_months)


class ProcessSubscriptionPaymentView(LoginRequiredMixin, View):
    """
    Обробка оплати підписки через LiqPay
    """
    
    def post(self, request, plan_id):
        plan = get_object_or_404(Plan, id=plan_id, is_active=True)
        user = request.user
        
        # Перевіряємо промокод якщо є
        coupon_code = request.POST.get('coupon_code', '').strip()
        coupon = None
        
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                if not coupon.can_be_used_by(user):
                    return JsonResponse({
                        'success': False,
                        'error': 'Цей промокод не може бути використаний'
                    })
            except Coupon.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Невірний промокод'
                })
        
        # Створюємо платіж через LiqPay
        liqpay_service = LiqPayService()
        
        return_url = request.build_absolute_uri(
            reverse('subscriptions:payment_success')
        )
        callback_url = request.build_absolute_uri(
            reverse('subscriptions:payment_callback')
        )
        
        try:
            payment_data = liqpay_service.create_subscription_payment(
                user=user,
                plan=plan,
                return_url=return_url,
                callback_url=callback_url
            )
            
            # Застосовуємо промокод якщо є
            if coupon:
                order = payment_data['payment'].order
                order.coupon = coupon
                order.calculate_totals()
            
            return JsonResponse({
                'success': True,
                'payment_id': payment_data['payment'].id,
                'liqpay_data': payment_data['data'],
                'liqpay_signature': payment_data['signature'],
                'liqpay_html': payment_data['html']
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })


class SubscriptionPaymentCallbackView(View):
    """
    Callback від LiqPay після оплати
    """
    
    def post(self, request):
        data = request.POST.get('data')
        signature = request.POST.get('signature')
        
        if not data or not signature:
            return JsonResponse({'status': 'error', 'message': 'Missing data'}, status=400)
        
        liqpay_service = LiqPayService()
        result = liqpay_service.handle_callback(data, signature)
        
        return JsonResponse(result)


class SubscriptionPaymentSuccessView(LoginRequiredMixin, TemplateView):
    """
    Сторінка успішної оплати підписки
    """
    template_name = 'subscriptions/payment_success.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Отримуємо останню активну підписку
        subscription = self.request.user.subscriptions.filter(
            status='active'
        ).order_by('-created_at').first()
        
        context['subscription'] = subscription
        context['redirect_url'] = reverse('cabinet:subscription')
        context['redirect_seconds'] = 5
        
        return context


class SubscriptionPaymentFailureView(LoginRequiredMixin, TemplateView):
    """
    Сторінка невдалої оплати підписки
    """
    template_name = 'subscriptions/payment_failure.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Отримуємо інформацію про помилку
        error_code = self.request.GET.get('error_code', '')
        error_message = self.request.GET.get('error_message', 'Відмова банку')
        
        context['error_code'] = error_code
        context['error_message'] = error_message
        context['retry_url'] = reverse('subscriptions:pricing')
        
        # Додаємо можливі причини помилок
        error_descriptions = {
            'insufficient_funds': 'Недостатньо коштів на картці',
            'card_declined': 'Картка відхилена банком',
            'invalid_card': 'Невірні дані картки',
            'timeout': 'Час очікування минув',
            'general_error': 'Загальна помилка системи'
        }
        
        context['error_description'] = error_descriptions.get(
            error_code,
            error_message
        )
        
        return context


class ValidateCouponView(LoginRequiredMixin, View):
    """
    AJAX перевірка промокоду
    """
    
    def post(self, request):
        coupon_code = request.POST.get('code', '').strip()
        
        if not coupon_code:
            return JsonResponse({
                'valid': False,
                'error': 'Введіть промокод'
            })
        
        try:
            coupon = Coupon.objects.get(code=coupon_code, is_active=True)
            
            if not coupon.can_be_used_by(request.user):
                return JsonResponse({
                    'valid': False,
                    'error': 'Цей промокод не може бути використаний'
                })
            
            return JsonResponse({
                'valid': True,
                'discount': coupon.get_discount_display(),
                'description': coupon.description
            })
            
        except Coupon.DoesNotExist:
            return JsonResponse({
                'valid': False,
                'error': 'Невірний промокод'
            })

