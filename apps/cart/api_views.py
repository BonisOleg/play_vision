from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from apps.content.models import Course
from apps.subscriptions.models import Plan


class CartMixin:
    """Mixin to get or create cart for API views"""
    
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


class CartAddAPIView(CartMixin, APIView):
    """Add item to cart via API"""
    
    def post(self, request):
        cart = self.get_cart(request)
        item_type = request.data.get('item_type')
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity', 1)
        
        if not item_type or not item_id:
            return Response(
                {'error': 'item_type and item_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            if item_type == 'course':
                course = Course.objects.get(id=item_id, is_published=True)
                cart.add_course(course, quantity)
                item_name = course.title
            elif item_type == 'subscription':
                plan = Plan.objects.get(id=item_id, is_active=True)
                cart.add_subscription(plan)
                item_name = plan.name
            else:
                return Response(
                    {'error': 'Invalid item type'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response({
                'success': True,
                'message': f'{item_name} додано в кошик',
                'cart_count': cart.get_items_count(),
                'cart_total': float(cart.get_total())
            })
            
        except (Course.DoesNotExist, Plan.DoesNotExist):
            return Response(
                {'error': 'Item not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class CartRemoveAPIView(CartMixin, APIView):
    """Remove item from cart via API"""
    
    def post(self, request):
        cart = self.get_cart(request)
        item_id = request.data.get('item_id')
        
        if not item_id:
            return Response(
                {'error': 'item_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            item = cart.items.get(id=item_id)
            item_name = item.item_name
            item.delete()
            
            return Response({
                'success': True,
                'message': f'{item_name} видалено з кошика',
                'cart_count': cart.get_items_count(),
                'cart_total': float(cart.get_total())
            })
            
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Item not found in cart'},
                status=status.HTTP_404_NOT_FOUND
            )


class CartUpdateAPIView(CartMixin, APIView):
    """Update cart item quantity via API"""
    
    def post(self, request):
        cart = self.get_cart(request)
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity')
        
        if not item_id or quantity is None:
            return Response(
                {'error': 'item_id and quantity are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            item = cart.items.get(id=item_id)
            
            if quantity <= 0:
                item.delete()
                message = f'{item.item_name} видалено з кошика'
            else:
                item.quantity = quantity
                item.save()
                message = f'Кількість оновлено'
            
            return Response({
                'success': True,
                'message': message,
                'cart_count': cart.get_items_count(),
                'cart_total': float(cart.get_total())
            })
            
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Item not found in cart'},
                status=status.HTTP_404_NOT_FOUND
            )


class CartCountAPIView(CartMixin, APIView):
    """Get cart items count"""
    
    def get(self, request):
        cart = self.get_cart(request)
        return Response({
            'count': cart.get_items_count(),
            'total': float(cart.get_total())
        })
