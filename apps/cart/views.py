from django.views.generic import TemplateView, View
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from .models import Cart, CartItem
from .services import CartService, SubscriptionSuggestionService
from apps.content.models import Course
from apps.subscriptions.models import Plan


class CartMixin:
    """Mixin to get or create cart"""
    
    def get_cart(self):
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
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


class CartView(CartMixin, TemplateView):
    """Shopping cart view"""
    template_name = 'cart/cart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = self.get_cart()
        context['cart'] = cart
        context['cart_items'] = cart.items.all()
        context['cart_total'] = cart.get_total()
        
        # Check if we should show subscription suggestion
        suggestion_service = SubscriptionSuggestionService()
        if suggestion_service.should_show_suggestion(cart, self.request.user):
            context['show_suggestion'] = True
            context['suggestion_data'] = suggestion_service.get_suggestion_data(cart)
        
        # Get recommendations
        context['recommendations'] = self.get_recommendations(cart)
        
        return context
    
    def get_recommendations(self, cart):
        """Get product recommendations for cart"""
        # Simple recommendation logic - get popular courses not in cart
        cart_course_ids = cart.items.filter(
            item_type='course'
        ).values_list('item_id', flat=True)
        
        recommendations = Course.objects.filter(
            is_published=True,
            is_featured=True
        ).exclude(id__in=cart_course_ids)[:2]
        
        return recommendations


class AddToCartView(CartMixin, View):
    """Add item to cart"""
    
    def post(self, request, item_type, item_id):
        cart = self.get_cart()
        
        if item_type == 'course':
            course = get_object_or_404(Course, id=item_id)
            cart.add_course(course)
            item_name = course.title
        elif item_type == 'subscription':
            plan = get_object_or_404(Plan, id=item_id)
            cart.add_subscription(plan)
            item_name = plan.name
        else:
            return JsonResponse({'error': 'Invalid item type'}, status=400)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'{item_name} додано в кошик',
                'cart_count': cart.get_items_count(),
                'cart_total': float(cart.get_total())
            })
        
        messages.success(request, f'{item_name} додано в кошик')
        return redirect('cart:cart')


class RemoveFromCartView(CartMixin, View):
    """Remove item from cart"""
    
    def post(self, request, item_id):
        cart = self.get_cart()
        
        try:
            item = cart.items.get(id=item_id)
            item_name = item.item_name
            item.delete()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': f'{item_name} видалено з кошика',
                    'cart_count': cart.get_items_count(),
                    'cart_total': float(cart.get_total())
                })
            
            messages.success(request, f'{item_name} видалено з кошика')
        except CartItem.DoesNotExist:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Item not found'}, status=404)
            messages.error(request, 'Товар не знайдено в кошику')
        
        return redirect('cart:cart')


class ClearCartView(CartMixin, View):
    """Clear all items from cart"""
    
    def post(self, request):
        cart = self.get_cart()
        cart.clear()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Кошик очищено',
                'cart_count': 0,
                'cart_total': 0
            })
        
        messages.success(request, 'Кошик очищено')
        return redirect('cart:cart')


class SubscriptionSuggestionView(CartMixin, View):
    """Get subscription suggestion data via AJAX"""
    
    def get(self, request):
        cart = self.get_cart()
        suggestion_service = SubscriptionSuggestionService()
        
        if suggestion_service.should_show_suggestion(cart, request.user):
            data = suggestion_service.get_suggestion_data(cart)
            return JsonResponse(data)
        
        return JsonResponse({'show_suggestion': False})