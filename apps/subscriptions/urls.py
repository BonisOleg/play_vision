from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    # Pricing page
    path('pricing/', views.PricingView.as_view(), name='pricing'),
    
    # Subscription management
    path('subscribe/<int:plan_id>/', views.SubscribeView.as_view(), name='subscribe'),
    path('cancel/', views.CancelSubscriptionView.as_view(), name='cancel'),
    path('reactivate/', views.ReactivateSubscriptionView.as_view(), name='reactivate'),
    
    # Plan details
    path('plan/<int:plan_id>/', views.PlanDetailView.as_view(), name='plan_detail'),
]
