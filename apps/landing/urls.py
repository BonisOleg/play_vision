from django.urls import path
from . import views

app_name = 'landing'

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('submit/', views.submit_lead, name='submit_lead'),
    path('hub/lead-form/', views.hub_lead_form_page, name='hub_lead_form'),
    path('mentoring/lead-form/', views.mentoring_lead_form_page, name='mentoring_lead_form'),
    path('subscription/lead-form/', views.subscription_lead_form_page, name='subscription_lead_form'),
]

