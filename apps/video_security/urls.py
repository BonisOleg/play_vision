from django.urls import path
from . import views

app_name = 'video_security'

urlpatterns = [
    # Захищена доставка відео
    path('secure-video/<int:material_id>/', views.SecureVideoView.as_view(), name='secure_video'),
    
    # API endpoint для отримання захищеного URL
    path('api/secure-url/<int:material_id>/', views.SecureVideoURLView.as_view(), name='secure_url'),
    
    # Завантаження відео в S3 (тільки для адміністраторів)
    path('upload-video/<int:material_id>/', views.VideoUploadView.as_view(), name='upload_video'),
    
    # Статистика безпеки (тільки для адміністраторів)
    path('stats/', views.SecurityStatsView.as_view(), name='security_stats'),
    
    # Демо сторінка для тестування (НОВИЙ)
    path('demo/', views.SecureVideoDemoView.as_view(), name='demo'),
]
