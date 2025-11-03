from django.urls import path
from . import views

app_name = 'mentoring'

urlpatterns = [
    path('', views.mentoring_page, name='mentoring_page'),
]

