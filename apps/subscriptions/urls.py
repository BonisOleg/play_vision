"""
URL маршрути для підписок
"""
from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('pricing/', views.PricingView.as_view(), name='pricing'),
]

