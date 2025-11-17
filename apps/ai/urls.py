from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    # AI Chat interface (заглушка)
    path('chat/', views.AIChatView.as_view(), name='chat'),
]
