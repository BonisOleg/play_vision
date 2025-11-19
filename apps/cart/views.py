from django.views.generic import TemplateView, View
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from .models import Cart, CartItem
from .services import CartService, SubscriptionSuggestionService
from apps.content.models import Course
# TODO: Нова система підписок  
from apps.subscriptions.models import SubscriptionPlan as Plan


class CartView(TemplateView):
    """Shopping cart view"""
    template_name = 'cart/cart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Use CartService for all cart operations
        cart_service = CartService(self.request)
        cart = cart_service.cart
        
        context['cart'] = cart
        context['cart_items'] = cart.items.all()
        context['cart_subtotal'] = cart.get_subtotal()
        context['cart_discount'] = cart.discount_amount
        context['cart_tips'] = cart.tips_amount
        context['cart_total'] = cart.get_total_with_discount()
        
        # Applied coupon info
        if cart.applied_coupon:
            context['applied_coupon'] = cart.applied_coupon
            context['discount_percentage'] = cart.get_discount_percentage()
        
        # Subscription suggestion
        suggestion_service = SubscriptionSuggestionService()
        if suggestion_service.should_show_suggestion(cart, self.request.user):
            context['show_suggestion'] = True
            context['suggestion_data'] = suggestion_service.get_suggestion_data(cart)
        
        # Product recommendations
        context['recommendations'] = cart_service.get_recommendations()
        
        return context


class AddToCartView(View):
    """Add item to cart"""
    
    def post(self, request, item_type, item_id):
        cart_service = CartService(request)
        
        if item_type == 'course':
            course = get_object_or_404(Course, id=item_id)
            success, message = cart_service.add_course(course)
        elif item_type == 'subscription':
            plan = get_object_or_404(Plan, id=item_id)
            success, message = cart_service.add_subscription(plan)
        else:
            success, message = False, 'Невірний тип товару'
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': success,
                'message': message,
                'cart_count': cart_service.get_items_count(),
                'cart_total': float(cart_service.cart.get_total_with_discount())
            })
        
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
            
        return redirect('cart:cart')


class RemoveFromCartView(View):
    """Remove item from cart"""
    
    def post(self, request, item_id):
        cart_service = CartService(request)
        success, message = cart_service.remove_item(item_id)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': success,
                'message': message,
                'cart_count': cart_service.get_items_count() if success else 0,
                'cart_total': float(cart_service.cart.get_total_with_discount()) if success else 0
            })
        
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
            
        return redirect('cart:cart')


class ClearCartView(View):
    """Clear all items from cart"""
    
    def post(self, request):
        cart_service = CartService(request)
        success, message = cart_service.clear()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': success,
                'message': message,
                'cart_count': 0,
                'cart_total': 0
            })
        
        messages.success(request, message)
        return redirect('cart:cart')


class SubscriptionSuggestionView(View):
    """Get subscription suggestion data via AJAX"""
    
    def get(self, request):
        cart_service = CartService(request)
        suggestion_service = SubscriptionSuggestionService()
        
        if suggestion_service.should_show_suggestion(cart_service.cart, request.user):
            data = suggestion_service.get_suggestion_data(cart_service.cart)
            return JsonResponse(data)
        
        return JsonResponse({'show_suggestion': False})


class ApplyCouponView(View):
    """Apply coupon to cart"""
    
    def post(self, request):
        cart_service = CartService(request)
        coupon_code = request.POST.get('coupon_code', '').strip()
        
        if not coupon_code:
            return JsonResponse({
                'success': False,
                'message': 'Введіть промокод'
            })
        
        success, message = cart_service.apply_coupon(coupon_code)
        
        response_data = {
            'success': success,
            'message': message
        }
        
        if success:
            cart = cart_service.cart
            response_data.update({
                'subtotal': float(cart.get_subtotal()),
                'discount': float(cart.discount_amount),
                'total': float(cart.get_total_with_discount()),
                'discount_percentage': cart.get_discount_percentage()
            })
        
        return JsonResponse(response_data)


class UpdateQuantityView(View):
    """Update item quantity in cart"""
    
    def post(self, request):
        cart_service = CartService(request)
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        
        success, message = cart_service.update_quantity(item_id, quantity)
        
        response_data = {
            'success': success,
            'message': message
        }
        
        if success:
            cart = cart_service.cart
            response_data.update({
                'cart_count': cart_service.get_items_count(),
                'cart_total': float(cart.get_total_with_discount())
            })
        
        return JsonResponse(response_data)