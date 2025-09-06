from django.urls import path
from . import htmx_views

app_name = 'cart_htmx'

urlpatterns = [
    path('add-to-cart/', htmx_views.HTMXAddToCartView.as_view(), name='add_to_cart'),
    path('cart-count/', htmx_views.HTMXCartCountView.as_view(), name='cart_count'),
    path('cart-items/', htmx_views.HTMXCartItemsView.as_view(), name='cart_items'),
    path('suggestion/', htmx_views.HTMXSubscriptionSuggestionView.as_view(), name='subscription_suggestion'),
]
