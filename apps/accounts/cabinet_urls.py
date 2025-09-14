from django.urls import path
from . import cabinet_views

app_name = 'cabinet'

urlpatterns = [
    # Головна сторінка кабінету (профіль за замовчуванням)
    path('', cabinet_views.CabinetView.as_view(), {'tab': 'profile'}, name='dashboard'),
    
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
    path('profile/update/', cabinet_views.UpdateProfileView.as_view(), name='update_profile'),
    path('profile/change-password/', cabinet_views.ChangePasswordView.as_view(), name='change_password'),
    path('api/toggle-favorite/', cabinet_views.ToggleFavoriteView.as_view(), name='toggle_favorite'),
    path('api/material-progress/', cabinet_views.UpdateMaterialProgressView.as_view(), name='material_progress'),
    
    # Керування підпискою
    path('subscription/cancel/', cabinet_views.CancelSubscriptionView.as_view(), name='cancel_subscription'),
    path('subscription/renew/', cabinet_views.RenewSubscriptionView.as_view(), name='renew_subscription'),
    path('subscription/change/', cabinet_views.ChangeSubscriptionView.as_view(), name='change_subscription'),
    
    # Лояльність та курси
    path('loyalty/add-points/', cabinet_views.AddLoyaltyPointsView.as_view(), name='add_loyalty_points'),
    path('course/complete/', cabinet_views.MarkCourseCompleteView.as_view(), name='mark_course_complete'),
    path('download/<int:material_id>/', cabinet_views.DownloadMaterialView.as_view(), name='download_material'),
]