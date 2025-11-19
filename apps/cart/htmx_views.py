from django.views.generic import View
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404
from django_htmx.http import HttpResponseClientRefresh
from .models import Cart, CartItem
from .services import SubscriptionSuggestionService
from apps.content.models import Course
from apps.subscriptions.models import SubscriptionPlan as Plan


class CartMixin:
    """Mixin to get or create cart for HTMX views"""
    
    def get_cart(self, request):
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            cart_id = request.session.get('cart_id')
            if cart_id:
                try:
                    cart = Cart.objects.get(id=cart_id, user=None)
                except Cart.DoesNotExist:
                    cart = Cart.objects.create()
                    request.session['cart_id'] = cart.id
            else:
                cart = Cart.objects.create()
                request.session['cart_id'] = cart.id
        return cart


class HTMXAddToCartView(CartMixin, View):
    """HTMX view to add item to cart"""
    
    def post(self, request):
        cart = self.get_cart(request)
        item_type = request.POST.get('item_type')
        item_id = request.POST.get('item_id')
        
        if item_type == 'course':
            course = get_object_or_404(Course, id=item_id)
            cart.add_course(course)
            item_name = course.title
        elif item_type == 'subscription':
            plan = get_object_or_404(Plan, id=item_id)
            cart.add_subscription(plan)
            item_name = plan.name
        else:
            return TemplateResponse(
                request,
                'htmx/error.html',
                {'message': 'Invalid item type'}
            )
        
        # Return updated cart count
        return TemplateResponse(
            request,
            'htmx/cart_count.html',
            {
                'cart_count': cart.get_items_count(),
                'message': f'{item_name} додано в кошик'
            }
        )


class HTMXCartCountView(CartMixin, View):
    """HTMX view to get cart count"""
    
    def get(self, request):
        cart = self.get_cart(request)
        return TemplateResponse(
            request,
            'htmx/cart_count.html',
            {'cart_count': cart.get_items_count()}
        )


class HTMXCartItemsView(CartMixin, View):
    """HTMX view to get cart items"""
    
    def get(self, request):
        cart = self.get_cart(request)
        return TemplateResponse(
            request,
            'htmx/cart_items.html',
            {
                'cart': cart,
                'cart_items': cart.items.all(),
                'cart_total': cart.get_total()
            }
        )
    
    def delete(self, request):
        """Remove item from cart"""
        cart = self.get_cart(request)
        item_id = request.POST.get('item_id')
        
        try:
            item = cart.items.get(id=item_id)
            item.delete()
        except CartItem.DoesNotExist:
            pass
        
        # Return updated cart items
        return self.get(request)


class HTMXSubscriptionSuggestionView(CartMixin, View):
    """HTMX view for subscription suggestion"""
    
    def get(self, request):
        cart = self.get_cart(request)
        suggestion_service = SubscriptionSuggestionService()
        
        if suggestion_service.should_show_suggestion(cart, request.user):
            suggestion_data = suggestion_service.get_suggestion_data(cart)
            return TemplateResponse(
                request,
                'htmx/subscription_suggestion.html',
                {'suggestion': suggestion_data}
            )
        
        # Return empty response if no suggestion
        return TemplateResponse(
            request,
            'htmx/empty.html',
            {}
        )
