"""
LiqPay Payment Service
Обробка платежів через LiqPay API (жовтень 2025)
"""
import base64
import hashlib
import json
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from liqpay import LiqPay

from .models import Payment, Order, OrderItem
from apps.subscriptions.models import Subscription, Plan


class LiqPayService:
    """
    Сервіс для роботи з LiqPay API
    Підтримує: одноразові платежі, підписки, Apple/Google Pay
    """
    
    def __init__(self):
        self.public_key = settings.LIQPAY_PUBLIC_KEY
        self.private_key = settings.LIQPAY_PRIVATE_KEY
        self.sandbox = settings.LIQPAY_SANDBOX
        self.liqpay = LiqPay(self.public_key, self.private_key)
    
    def create_payment(self, order, return_url, callback_url):
        """
        Створення платежу в LiqPay
        
        Args:
            order: Order instance
            return_url: URL для повернення після оплати
            callback_url: URL для callback від LiqPay
            
        Returns:
            dict: {'data': data, 'signature': signature, 'html': html_form}
        """
        # Створюємо Payment запис
        payment = Payment.objects.create(
            user=order.user,
            amount=order.total,
            currency='UAH',
            status='pending',
            payment_type=self._get_payment_type(order),
            description=self._generate_description(order)
        )
        
        order.payment = payment
        order.status = 'pending'
        order.save()
        
        # Параметри для LiqPay
        params = {
            'version': '3',
            'action': 'pay',
            'amount': float(order.total),
            'currency': 'UAH',
            'description': payment.description,
            'order_id': order.order_number,
            'result_url': return_url,
            'server_url': callback_url,
            'sandbox': 1 if self.sandbox else 0,
        }
        
        # Додаємо підтримку підписок для рекурентних платежів
        if self._is_subscription_order(order):
            params['subscribe'] = '1'
            params['subscribe_periodicity'] = 'month'
        
        # Генеруємо форму оплати
        data = base64.b64encode(json.dumps(params).encode('utf-8')).decode('ascii')
        signature = self._generate_signature(data)
        
        # Зберігаємо дані в payment
        payment.metadata = {
            'liqpay_data': data,
            'liqpay_signature': signature,
            'order_number': order.order_number
        }
        payment.save()
        
        return {
            'payment': payment,
            'data': data,
            'signature': signature,
            'html': self._generate_payment_form(data, signature)
        }
    
    def _generate_signature(self, data):
        """Генерація підпису для LiqPay"""
        sign_string = self.private_key + data + self.private_key
        return base64.b64encode(
            hashlib.sha1(sign_string.encode('utf-8')).digest()
        ).decode('ascii')
    
    def _generate_payment_form(self, data, signature):
        """Генерація HTML форми для оплати"""
        return f'''
        <form method="POST" action="https://www.liqpay.ua/api/3/checkout" accept-charset="utf-8" id="liqpay-form">
            <input type="hidden" name="data" value="{data}" />
            <input type="hidden" name="signature" value="{signature}" />
        </form>
        <script>
            document.getElementById('liqpay-form').submit();
        </script>
        '''
    
    def handle_callback(self, data, signature):
        """
        Обробка callback від LiqPay
        
        Args:
            data: base64 encoded JSON з даними платежу
            signature: підпис для перевірки
            
        Returns:
            dict: результат обробки
        """
        # Перевіряємо підпис
        if not self._verify_signature(data, signature):
            return {'status': 'error', 'message': 'Invalid signature'}
        
        # Декодуємо дані
        decoded_data = base64.b64decode(data).decode('utf-8')
        payment_data = json.loads(decoded_data)
        
        order_number = payment_data.get('order_id')
        status = payment_data.get('status')
        
        try:
            order = Order.objects.get(order_number=order_number)
            payment = order.payment
            
            # Оновлюємо статус платежу
            payment.provider_response = payment_data
            
            if status == 'success':
                return self._handle_successful_payment(payment, order, payment_data)
            elif status == 'failure' or status == 'error':
                return self._handle_failed_payment(payment, order, payment_data)
            else:
                payment.status = 'processing'
                payment.save()
                return {'status': 'processing', 'order_id': order_number}
                
        except Order.DoesNotExist:
            return {'status': 'error', 'message': 'Order not found'}
    
    def _verify_signature(self, data, signature):
        """Перевірка підпису від LiqPay"""
        expected_signature = self._generate_signature(data)
        return signature == expected_signature
    
    @transaction.atomic
    def _handle_successful_payment(self, payment, order, payment_data):
        """Обробка успішного платежу"""
        payment.status = 'succeeded'
        payment.completed_at = timezone.now()
        payment.payment_method = payment_data.get('paytype', 'card')
        payment.save()
        
        order.status = 'completed'
        order.completed_at = timezone.now()
        order.save()
        
        # Обробляємо товари замовлення
        self._process_order_items(order)
        
        # Нараховуємо loyalty points
        self._award_loyalty_points(order)
        
        # Оновлюємо промокод
        if order.coupon:
            order.coupon.used_count += 1
            order.coupon.save()
        
        return {
            'status': 'success',
            'order_id': order.order_number,
            'payment_id': payment.id
        }
    
    def _handle_failed_payment(self, payment, order, payment_data):
        """Обробка невдалого платежу"""
        payment.status = 'failed'
        payment.save()
        
        order.status = 'failed'
        order.save()
        
        error_message = payment_data.get('err_description', 'Помилка оплати')
        
        return {
            'status': 'failed',
            'order_id': order.order_number,
            'error': error_message
        }
    
    def _process_order_items(self, order):
        """Обробка товарів після успішної оплати"""
        for item in order.items.all():
            if item.item_type == 'course':
                self._grant_course_access(order.user, item.item_id)
            elif item.item_type == 'subscription':
                self._create_subscription(order.user, item.item_id)
            elif item.item_type == 'event_ticket':
                self._create_event_ticket(order.user, item.item_id, order.payment)
    
    def _grant_course_access(self, user, course_id):
        """Надання доступу до курсу"""
        from apps.content.models import Course, UserCourseAccess
        
        course = Course.objects.get(id=course_id)
        UserCourseAccess.objects.get_or_create(
            user=user,
            course=course,
            defaults={
                'granted_at': timezone.now(),
                'access_type': 'purchased'
            }
        )
    
    def _create_subscription(self, user, plan_id):
        """Створення підписки після оплати"""
        plan = Plan.objects.get(id=plan_id)
        
        # Визначаємо дати
        start_date = timezone.now()
        end_date = start_date + timedelta(days=30 * plan.duration_months)
        
        # Створюємо підписку
        subscription = Subscription.objects.create(
            user=user,
            plan=plan,
            status='active',
            start_date=start_date,
            end_date=end_date,
            auto_renew=True
        )
        
        return subscription
    
    def _create_event_ticket(self, user, event_id, payment):
        """Створення квитка на івент"""
        from apps.events.models import Event, EventRegistration
        
        event = Event.objects.get(id=event_id)
        EventRegistration.objects.create(
            user=user,
            event=event,
            payment=payment,
            status='confirmed'
        )
    
    def _award_loyalty_points(self, order):
        """Нарахування балів лояльності"""
        try:
            from apps.loyalty.services import LoyaltyService
            loyalty_service = LoyaltyService()
            loyalty_service.award_purchase_points(
                user=order.user,
                amount=order.total
            )
        except Exception:
            pass  # Loyalty не обов'язкова
    
    def _get_payment_type(self, order):
        """Визначення типу платежу з замовлення"""
        if order.items.filter(item_type='subscription').exists():
            return 'subscription'
        elif order.items.filter(item_type='course').exists():
            return 'course'
        elif order.items.filter(item_type='event_ticket').exists():
            return 'event_ticket'
        return 'bundle'
    
    def _generate_description(self, order):
        """Генерація опису платежу"""
        items = order.items.all()
        if items.count() == 1:
            return f"Оплата: {items[0].item_name}"
        return f"Оплата замовлення #{order.order_number}"
    
    def _is_subscription_order(self, order):
        """Перевірка чи це замовлення підписки"""
        return order.items.filter(item_type='subscription').exists()
    
    def create_subscription_payment(self, user, plan, return_url, callback_url):
        """
        Створення платежу для підписки з рекурентними списаннями
        
        Args:
            user: User instance
            plan: Plan instance
            return_url: URL повернення
            callback_url: URL callback
            
        Returns:
            dict: дані для форми оплати
        """
        # Створюємо Order для підписки
        from .models import Order, OrderItem
        import uuid
        
        order = Order.objects.create(
            user=user,
            order_number=f"SUB-{uuid.uuid4().hex[:12].upper()}",
            status='draft',
            subtotal=plan.price,
            total=plan.price
        )
        
        OrderItem.objects.create(
            order=order,
            item_type='subscription',
            item_id=plan.id,
            item_name=plan.name,
            quantity=1,
            price=plan.price,
            total=plan.price
        )
        
        order.calculate_totals()
        
        return self.create_payment(order, return_url, callback_url)

