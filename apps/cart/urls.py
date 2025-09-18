from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.CartView.as_view(), name='cart'),
    path('add/<str:item_type>/<int:item_id>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('remove/<int:item_id>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('clear/', views.ClearCartView.as_view(), name='clear_cart'),
    path('suggestion/', views.SubscriptionSuggestionView.as_view(), name='subscription_suggestion'),
    path('apply-coupon/', views.ApplyCouponView.as_view(), name='apply_coupon'),
    path('update-quantity/', views.UpdateQuantityView.as_view(), name='update_quantity'),
]
