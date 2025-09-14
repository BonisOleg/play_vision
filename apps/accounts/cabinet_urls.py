from django.urls import path
from . import cabinet_views

app_name = 'cabinet'

urlpatterns = [
    # Головна сторінка кабінету (дашборд за замовчуванням)
    path('', cabinet_views.CabinetView.as_view(), {'tab': 'dashboard'}, name='dashboard'),
    path('index/', cabinet_views.CabinetView.as_view(), {'tab': 'dashboard'}, name='index'),
    
    # Основні розділи кабінету
    path('profile/', cabinet_views.CabinetView.as_view(), {'tab': 'profile'}, name='profile'),
    path('subscription/', cabinet_views.CabinetView.as_view(), {'tab': 'subscription'}, name='subscription'),
    path('files/', cabinet_views.CabinetView.as_view(), {'tab': 'files'}, name='files'),
    path('courses/', cabinet_views.CabinetView.as_view(), {'tab': 'courses'}, name='courses'),
    path('events/', cabinet_views.CabinetView.as_view(), {'tab': 'events'}, name='events'),
    path('loyalty/', cabinet_views.CabinetView.as_view(), {'tab': 'loyalty'}, name='loyalty'),
    path('payments/', cabinet_views.CabinetView.as_view(), {'tab': 'payments'}, name='payments'),
    path('settings/', cabinet_views.CabinetView.as_view(), {'tab': 'settings'}, name='settings'),
    
    # AJAX endpoints для оновлення даних
    path('api/update-profile/', cabinet_views.UpdateProfileView.as_view(), name='update_profile'),
    path('api/change-password/', cabinet_views.ChangePasswordView.as_view(), name='change_password'),
    path('api/toggle-favorite/', cabinet_views.ToggleFavoriteView.as_view(), name='toggle_favorite'),
    path('api/material-progress/', cabinet_views.UpdateMaterialProgressView.as_view(), name='material_progress'),
    
    # Завантаження матеріалів для офлайну
    path('download/<int:material_id>/', cabinet_views.DownloadMaterialView.as_view(), name='download_material'),
]