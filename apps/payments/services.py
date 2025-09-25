import json
import hashlib
import hmac
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model

from .models import Payment, Order, OrderItem, WebhookEvent, Coupon, CouponUsage

User = get_user_model()

# Optional Stripe configuration
try:
    import stripe
    stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
    STRIPE_AVAILABLE = bool(settings.STRIPE_SECRET_KEY)
except ImportError:
    STRIPE_AVAILABLE = False


class PaymentService:
    """
    Main payment service for handling Stripe payments
    """
    
    def __init__(self):
        if STRIPE_AVAILABLE:
            self.stripe = stripe
        else:
            self.stripe = None
    
    def create_payment_intent(self, order, payment_method_id=None, customer_id=None):
        """Create Stripe payment intent with 3DS"""
        if not STRIPE_AVAILABLE or not self.stripe:
            raise Exception("Stripe is not configured or available")
        
        try:
            intent_data = {
                'amount': int(order.total * 100),  # Convert to cents
                'currency': 'uah',
                'metadata': {
                    'order_id': str(order.id),
                    'user_id': str(order.user.id) if order.user else '',
                    'order_number': order.order_number
                },
                'payment_method_options': {
                    'card': {
                        'request_three_d_secure': 'required'
                    }
                }
            }
            
            # Add customer if provided
            if customer_id:
                intent_data['customer'] = customer_id
            
            # Add payment method if provided
            if payment_method_id:
                intent_data['payment_method'] = payment_method_id
                intent_data['confirm'] = True
            
            intent = self.stripe.PaymentIntent.create(**intent_data)
            
            # Create payment record
            payment = Payment.objects.create(
                user=order.user,
                amount=order.total,
                status='pending',
                payment_type=self.get_order_payment_type(order),
                stripe_payment_intent_id=intent.id,
                payment_method=payment_method_id or '',
                requires_3ds=intent.status == 'requires_action',
                client_secret=intent.client_secret,
                description=f"Замовлення #{order.order_number}",
                metadata={
                    'order_id': order.id,
                    'stripe_intent_id': intent.id
                }
            )
            
            # Link payment to order
            order.payment = payment
            order.status = 'pending'
            order.save()
            
            return payment, intent
            
        except stripe.error.StripeError as e:
            raise PaymentError(f"Stripe error: {str(e)}")
    
    def handle_3ds_challenge(self, payment_intent_id):
        """Handle 3DS challenge response"""
        try:
            intent = self.stripe.PaymentIntent.retrieve(payment_intent_id)
            
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent_id)
            
            if intent.status == 'requires_action':
                payment.status = 'requires_action'
                payment.requires_3ds = True
                payment.save()
                
                return {
                    'requires_action': True,
                    'client_secret': intent.client_secret,
                    'payment_id': payment.id
                }
            elif intent.status == 'succeeded':
                self.handle_successful_payment(payment, intent)
                return {
                    'requires_action': False,
                    'status': 'succeeded',
                    'payment_id': payment.id
                }
            else:
                payment.status = 'failed'
                payment.save()
                return {
                    'requires_action': False,
                    'status': 'failed',
                    'error': 'Payment failed'
                }
                
        except Payment.DoesNotExist:
            raise PaymentError("Payment not found")
        except stripe.error.StripeError as e:
            raise PaymentError(f"Stripe error: {str(e)}")
    
    def handle_successful_payment(self, payment, stripe_intent=None):
        """Handle successful payment"""
        with transaction.atomic():
            # Update payment status
            payment.status = 'succeeded'
            payment.completed_at = timezone.now()
            if stripe_intent:
                payment.provider_response = stripe_intent
            payment.save()
            
            # Update order status
            order = payment.order
            order.status = 'completed'
            order.completed_at = timezone.now()
            order.save()
            
            # Process order items (grant access, create subscriptions, etc.)
            self.process_order_completion(order)
            
            # Update coupon usage if applicable
            if order.coupon:
                order.coupon.used_count += 1
                order.coupon.save()
                
                # Record usage
                CouponUsage.objects.create(
                    coupon=order.coupon,
                    user=order.user,
                    order=order
                )
    
    def process_order_completion(self, order):
        """Process completed order items"""
        for item in order.items.all():
            if item.item_type == 'course':
                self.grant_course_access(order.user, item.item_id)
            elif item.item_type == 'subscription':
                self.create_subscription(order.user, item.item_id)
            elif item.item_type == 'event_ticket':
                self.create_event_ticket(order.user, item.item_id, order.payment)
    
    def grant_course_access(self, user, course_id):
        """Grant user access to purchased course"""
        from apps.content.models import Course, UserCourseProgress
        
        try:
            course = Course.objects.get(id=course_id)
            # Create progress record to track access
            UserCourseProgress.objects.get_or_create(
                user=user,
                course=course,
                defaults={'started_at': timezone.now()}
            )
        except Course.DoesNotExist:
            pass
    
    def create_subscription(self, user, plan_id):
        """Create user subscription"""
        from apps.subscriptions.models import Plan, Subscription, Entitlement
        
        try:
            plan = Plan.objects.get(id=plan_id)
            
            # Calculate dates
            start_date = timezone.now()
            if plan.duration == '1_month':
                end_date = start_date + timezone.timedelta(days=30)
            elif plan.duration == '3_months':
                end_date = start_date + timezone.timedelta(days=90)
            elif plan.duration == '12_months':
                end_date = start_date + timezone.timedelta(days=365)
            
            # Create subscription
            subscription = Subscription.objects.create(
                user=user,
                plan=plan,
                status='active',
                start_date=start_date,
                end_date=end_date
            )
            
            # Create entitlements
            Entitlement.objects.create(
                subscription=subscription,
                content_type='course',
                content_id=None  # Access to all courses
            )
            
            # Grant ticket balance for Pro-Vision plans
            if plan.event_tickets_balance > 0:
                from apps.subscriptions.models import TicketBalance
                TicketBalance.objects.create(
                    user=user,
                    subscription=subscription,
                    amount=plan.event_tickets_balance,
                    expires_at=end_date
                )
                
        except Plan.DoesNotExist:
            pass
    
    def create_event_ticket(self, user, event_id, payment):
        """Create event ticket"""
        from apps.events.models import Event, EventTicket
        
        try:
            event = Event.objects.get(id=event_id)
            ticket = EventTicket.objects.create(
                event=event,
                user=user,
                payment=payment,
                status='confirmed'
            )
            
            # Update event ticket count
            event.tickets_sold += 1
            event.save()
            
        except Event.DoesNotExist:
            pass
    
    def get_order_payment_type(self, order):
        """Determine payment type from order items"""
        items = order.items.all()
        if items.filter(item_type='subscription').exists():
            return 'subscription'
        elif items.filter(item_type='event_ticket').exists():
            return 'event_ticket'
        elif items.filter(item_type='course').exists():
            return 'course'
        return 'bundle'
    
    def create_customer(self, user):
        """Create Stripe customer"""
        try:
            customer = self.stripe.Customer.create(
                email=user.email,
                name=user.profile.full_name if hasattr(user, 'profile') else user.email,
                metadata={'user_id': str(user.id)}
            )
            
            # Save customer ID
            user.stripe_customer_id = customer.id
            user.save()
            
            return customer
            
        except stripe.error.StripeError as e:
            raise PaymentError(f"Failed to create customer: {str(e)}")
    
    def get_or_create_customer(self, user):
        """Get existing or create new Stripe customer"""
        if user.stripe_customer_id:
            try:
                return self.stripe.Customer.retrieve(user.stripe_customer_id)
            except stripe.error.StripeError:
                # Customer not found, create new one
                pass
        
        return self.create_customer(user)


class WebhookService:
    """
    Service for handling Stripe webhooks
    """
    
    def __init__(self):
        self.stripe = stripe
        self.webhook_secret = settings.STRIPE_WEBHOOK_SECRET
    
    def verify_webhook_signature(self, payload, signature):
        """Verify webhook signature"""
        try:
            event = self.stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
            return event
        except ValueError:
            raise WebhookError("Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise WebhookError("Invalid signature")
    
    @transaction.atomic
    def handle_webhook(self, payload, signature):
        """Handle webhook with idempotency"""
        # Verify signature
        event = self.verify_webhook_signature(payload, signature)
        
        # Check for duplicate processing
        webhook_event, created = WebhookEvent.objects.get_or_create(
            event_id=event['id'],
            defaults={
                'event_type': event['type'],
                'payload': event,
                'processed': False
            }
        )
        
        if not created and webhook_event.processed:
            return {'status': 'duplicate', 'event_id': event['id']}
        
        try:
            # Process event
            result = self.process_webhook_event(event)
            
            # Mark as processed
            webhook_event.processed = True
            webhook_event.processed_at = timezone.now()
            webhook_event.save()
            
            return {
                'status': 'processed',
                'event_id': event['id'],
                'event_type': event['type'],
                'result': result
            }
            
        except Exception as e:
            webhook_event.error = str(e)
            webhook_event.save()
            raise WebhookError(f"Failed to process webhook: {str(e)}")
    
    def process_webhook_event(self, event):
        """Process specific webhook event types"""
        event_type = event['type']
        event_data = event['data']['object']
        
        handlers = {
            'payment_intent.succeeded': self.handle_payment_succeeded,
            'payment_intent.payment_failed': self.handle_payment_failed,
            'payment_intent.requires_action': self.handle_payment_requires_action,
            'customer.subscription.created': self.handle_subscription_created,
            'customer.subscription.updated': self.handle_subscription_updated,
            'customer.subscription.deleted': self.handle_subscription_deleted,
            'invoice.payment_succeeded': self.handle_invoice_payment_succeeded,
            'invoice.payment_failed': self.handle_invoice_payment_failed,
        }
        
        handler = handlers.get(event_type)
        if handler:
            return handler(event_data)
        
        return {'status': 'unhandled', 'type': event_type}
    
    def handle_payment_succeeded(self, payment_intent):
        """Handle successful payment"""
        try:
            payment = Payment.objects.get(
                stripe_payment_intent_id=payment_intent['id']
            )
            
            payment_service = PaymentService()
            payment_service.handle_successful_payment(payment, payment_intent)
            
            return {'status': 'success', 'payment_id': payment.id}
            
        except Payment.DoesNotExist:
            return {'status': 'payment_not_found'}
    
    def handle_payment_failed(self, payment_intent):
        """Handle failed payment"""
        try:
            payment = Payment.objects.get(
                stripe_payment_intent_id=payment_intent['id']
            )
            
            payment.status = 'failed'
            payment.provider_response = payment_intent
            payment.save()
            
            # Update order status
            if payment.order:
                payment.order.status = 'failed'
                payment.order.save()
            
            return {'status': 'failed', 'payment_id': payment.id}
            
        except Payment.DoesNotExist:
            return {'status': 'payment_not_found'}
    
    def handle_payment_requires_action(self, payment_intent):
        """Handle payment requiring action (3DS)"""
        try:
            payment = Payment.objects.get(
                stripe_payment_intent_id=payment_intent['id']
            )
            
            payment.status = 'requires_action'
            payment.requires_3ds = True
            payment.provider_response = payment_intent
            payment.save()
            
            return {'status': 'requires_action', 'payment_id': payment.id}
            
        except Payment.DoesNotExist:
            return {'status': 'payment_not_found'}
    
    def handle_subscription_created(self, subscription):
        """Handle subscription creation"""
        # This is for recurring subscriptions via Stripe
        # For now, we handle subscriptions differently
        return {'status': 'handled'}
    
    def handle_subscription_updated(self, subscription):
        """Handle subscription updates"""
        return {'status': 'handled'}
    
    def handle_subscription_deleted(self, subscription):
        """Handle subscription cancellation"""
        return {'status': 'handled'}
    
    def handle_invoice_payment_succeeded(self, invoice):
        """Handle successful invoice payment"""
        return {'status': 'handled'}
    
    def handle_invoice_payment_failed(self, invoice):
        """Handle failed invoice payment"""
        return {'status': 'handled'}


class CouponService:
    """
    Service for handling coupons and discounts
    """
    
    def validate_coupon(self, code, cart_total, user=None):
        """Validate coupon code"""
        try:
            coupon = Coupon.objects.get(
                code=code.upper(),
                is_active=True
            )
        except Coupon.DoesNotExist:
            return {'valid': False, 'error': 'Промокод не знайдено'}
        
        # Check validity period
        now = timezone.now()
        if now < coupon.valid_from or now > coupon.valid_until:
            return {'valid': False, 'error': 'Промокод не діє в цей період'}
        
        # Check minimum amount
        if cart_total < coupon.min_amount:
            return {
                'valid': False, 
                'error': f'Мінімальна сума замовлення: {coupon.min_amount} ₴'
            }
        
        # Check usage limits
        if coupon.max_uses and coupon.used_count >= coupon.max_uses:
            return {'valid': False, 'error': 'Промокод вичерпав ліміт використань'}
        
        # Check per-user usage
        if coupon.once_per_user and user:
            if CouponUsage.objects.filter(coupon=coupon, user=user).exists():
                return {'valid': False, 'error': 'Ви вже використовували цей промокод'}
        
        # Calculate discount
        if coupon.discount_type == 'percentage':
            discount = cart_total * (coupon.discount_value / 100)
        else:
            discount = min(coupon.discount_value, cart_total)
        
        return {
            'valid': True,
            'discount': discount,
            'coupon': coupon,
            'final_amount': cart_total - discount
        }
    
    def apply_coupon_to_order(self, order, coupon_code):
        """Apply coupon to order"""
        validation = self.validate_coupon(
            coupon_code, 
            order.subtotal, 
            order.user
        )
        
        if not validation['valid']:
            return validation
        
        coupon = validation['coupon']
        discount = validation['discount']
        
        # Apply to order
        order.coupon = coupon
        order.discount_amount = discount
        order.calculate_totals()
        
        return {
            'valid': True,
            'discount': discount,
            'message': f'Промокод застосовано! Знижка: {discount:.0f} ₴'
        }


class PaymentError(Exception):
    """Payment processing error"""
    pass


class WebhookError(Exception):
    """Webhook processing error"""
    pass
