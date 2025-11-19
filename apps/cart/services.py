from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
# TODO: Нова система підписок
# from apps.subscriptions.models import SubscriptionPlan as Plan
from apps.subscriptions.models import SubscriptionPlan as Plan
from apps.content.models import Course
from .models import Cart, CartItem


class CartService:
    """
    Main cart service for handling cart operations
    """
    
    def __init__(self, request):
        self.request = request
        self.user = request.user if request.user.is_authenticated else None
        self._cart = None
    
    @property
    def cart(self):
        """Get or create cart"""
        if self._cart is None:
            self._cart = self.get_or_create_cart()
        return self._cart
    
    def get_or_create_cart(self):
        """Get or create cart for current user/session"""
        if self.user:
            cart, created = Cart.objects.get_or_create(user=self.user)
            
            # Merge anonymous cart if exists
            anonymous_cart_id = self.request.session.get('cart_id')
            if anonymous_cart_id and created:
                try:
                    anonymous_cart = Cart.objects.get(id=anonymous_cart_id, user=None)
                    cart.merge_with(anonymous_cart)
                    del self.request.session['cart_id']
                except Cart.DoesNotExist:
                    pass
        else:
            cart_id = self.request.session.get('cart_id')
            if cart_id:
                try:
                    cart = Cart.objects.get(id=cart_id, user=None)
                except Cart.DoesNotExist:
                    cart = Cart.objects.create()
                    self.request.session['cart_id'] = cart.id
            else:
                cart = Cart.objects.create()
                self.request.session['cart_id'] = cart.id
        
        return cart
    
    def add_course(self, course, quantity=1):
        """Add course to cart with full metadata"""
        # Check if user already has access to this course
        if self.user and self.user.has_course_access(course):
            return False, "У вас вже є доступ до цього курсу"
        
        # Check if course is available for purchase
        if not course.is_published:
            return False, "Курс недоступний для покупки"
        
        # Generate display metadata
        metadata = {
            'tags': list(course.tags.values_list('name', flat=True)),
            'badges': self._get_course_badges(course),
            'duration': f"{course.duration_minutes} хв" if course.duration_minutes else '',
            'difficulty': course.get_difficulty_display() if hasattr(course, 'get_difficulty_display') else ''
        }
        
        content_type_display = self._get_course_content_type(course)
        thumbnail_url = course.thumbnail.url if hasattr(course, 'thumbnail') and course.thumbnail else ''
        
        # Add to cart with metadata
        item, created = self.cart.items.get_or_create(
            item_type='course',
            item_id=course.id,
            defaults={
                'item_name': course.title,
                'price': course.price,
                'quantity': quantity,
                'content_type_display': content_type_display,
                'thumbnail_url': thumbnail_url,
                'item_metadata': metadata
            }
        )
        
        if not created:
            item.quantity += quantity
            # Update metadata in case course was updated
            item.content_type_display = content_type_display
            item.thumbnail_url = thumbnail_url
            item.item_metadata = metadata
            item.save()
        
        return True, f"Курс '{course.title}' додано до кошика"
    
    def _get_course_badges(self, course):
        """Generate badges for course"""
        badges = []
        if hasattr(course, 'is_featured') and course.is_featured:
            badges.append('топ-продажів')
        if hasattr(course, 'created_at') and course.created_at > timezone.now() - timedelta(days=30):
            badges.append('новинка')
        return badges
    
    def _get_course_content_type(self, course):
        """Generate content type display for course"""
        if hasattr(course, 'materials'):
            materials = course.materials.all()
            video_materials = materials.filter(content_type='video')
            if video_materials.exists():
                total_duration = sum(m.video_duration_seconds for m in video_materials if m.video_duration_seconds)
                minutes = total_duration // 60
                return f"VIDEO • {minutes} ХВ"
            elif materials.filter(content_type='pdf').exists():
                return "PDF"
            elif materials.filter(content_type='article').exists():
                return "СТАТТЯ"
        return "КУРС"
    
    def add_subscription(self, plan):
        """Add subscription plan to cart"""
        # Check if user has active subscription
        if self.user and self.user.has_active_subscription():
            return False, "У вас вже є активна підписка"
        
        item = self.cart.add_subscription(plan)
        return True, f"План '{plan.name}' додано до кошика"
    
    def add_event_ticket(self, event, tier_name=None):
        """Add event ticket to cart"""
        # Check if user can register for event
        can_register, message = event.can_register(self.user)
        if not can_register:
            return False, message
        
        # Check if user already has ticket in cart
        existing_item = self.cart.items.filter(
            item_type='event_ticket',
            item_id=event.id
        ).first()
        
        if existing_item:
            return False, "Квиток на цей івент вже в кошику"
        
        # Determine price based on tier
        price = event.price
        tier_data = None
        
        if tier_name and event.ticket_tiers:
            for tier in event.ticket_tiers:
                if tier.get('name') == tier_name:
                    price = tier.get('price', event.price)
                    tier_data = tier
                    break
        
        # Prepare metadata
        metadata = {
            'tier_name': tier_name or '',
            'tier_features': tier_data.get('features', []) if tier_data else [],
            'event_date': event.start_datetime.isoformat(),
            'location': event.location
        }
        
        # Add to cart
        item = CartItem.objects.create(
            cart=self.cart,
            item_type='event_ticket',
            item_id=event.id,
            item_name=event.title,
            price=price,
            quantity=1,
            item_metadata=metadata
        )
        
        tier_display = f" ({tier_name})" if tier_name else ""
        return True, f"Квиток на '{event.title}'{tier_display} додано до кошика"
    
    def remove_item(self, item_id):
        """Remove item from cart"""
        try:
            item = self.cart.items.get(id=item_id)
            item_name = item.item_name
            item.delete()
            return True, f"'{item_name}' видалено з кошика"
        except CartItem.DoesNotExist:
            return False, "Товар не знайдено в кошику"
    
    def update_quantity(self, item_id, quantity):
        """Update item quantity"""
        try:
            item = self.cart.items.get(id=item_id)
            
            if quantity <= 0:
                return self.remove_item(item_id)
            
            # Only courses can have quantity > 1
            if item.item_type != 'course' and quantity > 1:
                return False, "Неможливо додати більше одного цього товару"
            
            item.quantity = quantity
            item.save()
            return True, "Кількість оновлено"
            
        except CartItem.DoesNotExist:
            return False, "Товар не знайдено в кошику"
    
    def clear(self):
        """Clear all items from cart"""
        self.cart.clear()
        return True, "Кошик очищено"
    
    def get_total(self):
        """Get cart total"""
        return self.cart.get_total()
    
    def get_items_count(self):
        """Get total items count"""
        return self.cart.get_items_count()
    
    def apply_coupon(self, coupon_code):
        """Apply coupon to cart"""
        from apps.payments.models import Coupon
        
        try:
            coupon = Coupon.objects.get(code=coupon_code.upper(), is_active=True)
        except Coupon.DoesNotExist:
            return False, "Промокод не знайдено"
        
        # Validate coupon
        if hasattr(coupon, 'can_be_used_by') and not coupon.can_be_used_by(self.user):
            return False, "Цей промокод не може бути використаний"
        
        # Check if coupon is valid
        if not coupon.is_valid:
            return False, "Промокод недійсний або закінчився"
        
        subtotal = self.cart.get_subtotal()
        if subtotal < coupon.min_amount:
            return False, f"Мінімальна сума замовлення: ${coupon.min_amount}"
        
        # Calculate discount
        if coupon.discount_type == 'percentage':
            discount = subtotal * (coupon.discount_value / 100)
        else:
            discount = min(coupon.discount_value, subtotal)
        
        # Apply to cart
        self.cart.applied_coupon = coupon
        self.cart.discount_amount = discount
        self.cart.save()
        
        return True, f"Промокод застосовано! Знижка: ${discount:.2f}"
    
    def remove_coupon(self):
        """Remove applied coupon"""
        self.cart.applied_coupon = None
        self.cart.discount_amount = 0
        self.cart.save()
        return True, "Промокод скасовано"
    
    def set_tips(self, tips_amount):
        """Set tips amount for authors"""
        if tips_amount >= 0:
            self.cart.tips_amount = Decimal(str(tips_amount))
            self.cart.save()
            return True, f"Чайові встановлено: ${tips_amount:.2f}"
        return False, "Некоректна сума чайових"
    
    def get_recommendations(self):
        """Get product recommendations based on cart contents"""
        recommendations = []
        
        # Get course IDs in cart
        cart_course_ids = self.cart.items.filter(
            item_type='course'
        ).values_list('item_id', flat=True)
        
        if cart_course_ids:
            # Get courses from same categories
            cart_courses = Course.objects.filter(id__in=cart_course_ids)
            category_ids = cart_courses.values_list('category_id', flat=True).distinct()
            
            related_courses = Course.objects.filter(
                category_id__in=category_ids,
                is_published=True
            ).exclude(id__in=cart_course_ids)[:3]
            
            recommendations.extend(related_courses)
        
        # Add featured courses if needed
        if len(recommendations) < 3:
            featured_courses = Course.objects.filter(
                is_featured=True,
                is_published=True
            ).exclude(id__in=cart_course_ids)[:3-len(recommendations)]
            
            recommendations.extend(featured_courses)
        
        return recommendations
    
    @transaction.atomic
    def prepare_checkout(self):
        """Prepare cart for checkout"""
        if not self.cart.items.exists():
            return False, "Кошик порожній"
        
        # Validate all items
        invalid_items = []
        
        for item in self.cart.items.all():
            if item.item_type == 'course':
                try:
                    course = Course.objects.get(id=item.item_id, is_published=True)
                    if self.user and self.user.has_course_access(course):
                        invalid_items.append(item)
                except Course.DoesNotExist:
                    invalid_items.append(item)
            
            elif item.item_type == 'subscription':
                try:
                    plan = Plan.objects.get(id=item.item_id, is_active=True)
                    if self.user and self.user.has_active_subscription():
                        invalid_items.append(item)
                except Plan.DoesNotExist:
                    invalid_items.append(item)
            
            elif item.item_type == 'event_ticket':
                try:
                    from apps.events.models import Event
                    event = Event.objects.get(id=item.item_id, status='published')
                    can_register, _ = event.can_register(self.user)
                    if not can_register:
                        invalid_items.append(item)
                except:
                    invalid_items.append(item)
        
        # Remove invalid items
        if invalid_items:
            for item in invalid_items:
                item.delete()
            
            if not self.cart.items.exists():
                return False, "Всі товари в кошику стали недоступними"
        
        return True, "Кошик готовий до оформлення"
    
    def create_order(self):
        """Create order from cart contents"""
        from apps.payments.models import Order, OrderItem
        import uuid
        
        success, message = self.prepare_checkout()
        if not success:
            return None, message
        
        # Generate order number
        order_number = f"PV{timezone.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}"
        
        # Create order
        order = Order.objects.create(
            user=self.user,
            order_number=order_number,
            status='draft'
        )
        
        # Create order items
        for cart_item in self.cart.items.all():
            OrderItem.objects.create(
                order=order,
                item_type=cart_item.item_type,
                item_id=cart_item.item_id,
                item_name=cart_item.item_name,
                quantity=cart_item.quantity,
                price=cart_item.price
            )
        
        # Calculate totals
        order.calculate_totals()
        
        return order, "Замовлення створено"


class SubscriptionSuggestionService:
    """
    Service for suggesting better subscription deals in cart
    """
    
    def should_show_suggestion(self, cart, user):
        """
        Check if we should show subscription suggestion
        """
        # Don't show if user has active subscription
        if user and user.is_authenticated and user.has_active_subscription():
            return False
        
        # Don't show if already shown in this session
        if cart.suggestion_shown:
            # Reset after 24 hours
            if cart.suggestion_shown_at and (timezone.now() - cart.suggestion_shown_at).days >= 1:
                cart.suggestion_shown = False
                cart.save()
            else:
                return False
        
        # Only show if cart has courses
        course_items = cart.items.filter(item_type='course')
        if not course_items.exists():
            return False
        
        # Show if cart total is more than 50% of monthly subscription
        cart_total = cart.get_total()
        monthly_plan = Plan.objects.filter(duration='1_month', is_active=True).first()
        
        if monthly_plan and cart_total > (monthly_plan.price * Decimal('0.5')):
            return True
        
        return False
    
    def get_suggestion_data(self, cart):
        """
        Get data for subscription suggestion display
        """
        cart_total = cart.get_subtotal()  # Використовуємо subtotal
        cart_items_count = cart.items.filter(item_type='course').count()
        
        # Знайти найкращий план для пропозиції
        # Приоритет: 3-місячний план якщо вартість кошика > $20
        if cart_total >= 20:
            suggested_plan = Plan.objects.filter(
                duration='3_months', 
                is_active=True
            ).first()
        else:
            # Інакше місячний план
            suggested_plan = Plan.objects.filter(
                duration='1_month',
                is_active=True  
            ).first()
        
        if suggested_plan:
            # Розрахунок економії
            potential_savings = max(cart_total - suggested_plan.price, 0)
            
            return {
                'show_suggestion': True,
                'plan': suggested_plan,
                'message': f"передплату за ${suggested_plan.price}/{suggested_plan.get_duration_display()}",
                'savings': potential_savings,
                'description': "це може бути вигідніше, ніж разові покупки."
            }
        
        return {'show_suggestion': False}
