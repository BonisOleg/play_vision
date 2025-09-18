from django.urls import path
from . import api_views

app_name = 'cart_api'

urlpatterns = [
    path('add/', api_views.CartAddAPIView.as_view(), name='add'),
    path('remove/', api_views.CartRemoveAPIView.as_view(), name='remove'),
    path('update/', api_views.CartUpdateAPIView.as_view(), name='update'),
    path('count/', api_views.CartCountAPIView.as_view(), name='count'),
    path('apply-coupon/', api_views.CartApplyCouponAPIView.as_view(), name='apply_coupon'),
]
