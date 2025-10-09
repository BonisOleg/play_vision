from django.urls import path
from . import views

app_name = 'loyalty'

urlpatterns = [
    path('rules/', views.LoyaltyRulesView.as_view(), name='rules'),
]

