from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .services import CartService
from apps.content.models import Course
from apps.subscriptions.models import SubscriptionPlan as Plan


class CartAddAPIView(APIView):
    """Add item to cart via API"""
    
    def post(self, request):
        cart_service = CartService(request)
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
                success, message = cart_service.add_course(course, quantity)
            elif item_type == 'subscription':
                plan = Plan.objects.get(id=item_id, is_active=True)
                success, message = cart_service.add_subscription(plan)
            else:
                return Response(
                    {'error': 'Invalid item type'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if success:
                return Response({
                    'success': True,
                    'message': message,
                    'cart_count': cart_service.get_items_count(),
                    'cart_total': float(cart_service.cart.get_total_with_discount())
                })
            else:
                return Response(
                    {'error': message},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
        except (Course.DoesNotExist, Plan.DoesNotExist):
            return Response(
                {'error': 'Item not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class CartRemoveAPIView(APIView):
    """Remove item from cart via API"""
    
    def post(self, request):
        cart_service = CartService(request)
        item_id = request.data.get('item_id')
        
        if not item_id:
            return Response(
                {'error': 'item_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success, message = cart_service.remove_item(item_id)
        
        if success:
            return Response({
                'success': True,
                'message': message,
                'cart_count': cart_service.get_items_count(),
                'cart_total': float(cart_service.cart.get_total_with_discount())
            })
        else:
            return Response(
                {'error': message},
                status=status.HTTP_404_NOT_FOUND
            )


class CartUpdateAPIView(APIView):
    """Update cart item quantity via API"""
    
    def post(self, request):
        cart_service = CartService(request)
        item_id = request.data.get('item_id')
        quantity = request.data.get('quantity')
        
        if not item_id or quantity is None:
            return Response(
                {'error': 'item_id and quantity are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success, message = cart_service.update_quantity(item_id, int(quantity))
        
        if success:
            return Response({
                'success': True,
                'message': message,
                'cart_count': cart_service.get_items_count(),
                'cart_total': float(cart_service.cart.get_total_with_discount())
            })
        else:
            return Response(
                {'error': message},
                status=status.HTTP_400_BAD_REQUEST
            )


class CartCountAPIView(APIView):
    """Get cart items count"""
    
    def get(self, request):
        cart_service = CartService(request)
        return Response({
            'count': cart_service.get_items_count(),
            'total': float(cart_service.cart.get_total_with_discount())
        })


class CartApplyCouponAPIView(APIView):
    """Apply coupon to cart via API"""
    
    def post(self, request):
        cart_service = CartService(request)
        coupon_code = request.data.get('code', '').strip()
        
        if not coupon_code:
            return Response(
                {'error': 'Coupon code is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
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
        
        return Response(response_data)
