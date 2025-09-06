from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Checkout flow
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('process/', views.PaymentProcessView.as_view(), name='process_payment'),
    path('confirm/', views.PaymentConfirmView.as_view(), name='confirm_payment'),
    
    # Coupon management
    path('apply-coupon/', views.ApplyCouponView.as_view(), name='apply_coupon'),
    path('remove-coupon/', views.RemoveCouponView.as_view(), name='remove_coupon'),
    path('validate-coupon/', views.validate_coupon, name='validate_coupon'),
    
    # Payment results
    path('success/<int:payment_id>/', views.PaymentSuccessView.as_view(), name='success'),
    path('failure/<int:payment_id>/', views.PaymentFailureView.as_view(), name='failure'),
    
    # Order management
    path('orders/', views.order_history, name='order_history'),
    path('order/<str:order_number>/', views.order_detail, name='order_detail'),
    
    # Payment methods
    path('payment-methods/', views.payment_methods, name='payment_methods'),
    path('detach-payment-method/', views.detach_payment_method, name='detach_payment_method'),
    
    # Webhooks
    path('webhook/stripe/', views.StripeWebhookView.as_view(), name='stripe_webhook'),
    
    # AJAX endpoints
    path('payment-status/<str:payment_intent_id>/', 
         views.get_payment_intent_status, 
         name='payment_status'),
]
