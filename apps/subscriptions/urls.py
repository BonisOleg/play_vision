from django.urls import path
from . import views, subscription_views

app_name = 'subscriptions'

urlpatterns = [
    # Pricing page
    path('pricing/', views.PricingView.as_view(), name='pricing'),
    
    # Subscription checkout flow (NEW)
    path('checkout/<int:plan_id>/', subscription_views.SubscriptionCheckoutView.as_view(), name='checkout'),
    path('process-payment/<int:plan_id>/', subscription_views.ProcessSubscriptionPaymentView.as_view(), name='process_payment'),
    path('payment-callback/', subscription_views.SubscriptionPaymentCallbackView.as_view(), name='payment_callback'),
    path('payment-success/', subscription_views.SubscriptionPaymentSuccessView.as_view(), name='payment_success'),
    path('payment-failure/', subscription_views.SubscriptionPaymentFailureView.as_view(), name='payment_failure'),
    path('validate-coupon/', subscription_views.ValidateCouponView.as_view(), name='validate_coupon'),
    
    # Old subscription management (kept for compatibility)
    path('subscribe/<int:plan_id>/', views.SubscribeView.as_view(), name='subscribe'),
    path('cancel/', views.CancelSubscriptionView.as_view(), name='cancel'),
    path('reactivate/', views.ReactivateSubscriptionView.as_view(), name='reactivate'),
    
    # Plan details
    path('plan/<int:plan_id>/', views.PlanDetailView.as_view(), name='plan_detail'),
]
