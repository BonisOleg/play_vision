"""
Context processors for cart functionality
"""
from .services import CartService


def cart_context(request):
    """
    Add cart context to all templates
    """
    cart_service = CartService(request)
    
    return {
        'cart_items_count': cart_service.get_items_count(),
        'cart_total_amount': cart_service.cart.get_total_with_discount(),
    }
