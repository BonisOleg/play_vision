"""
Кастомна структура адмінки з ієрархічною навігацією
"""
from django.contrib import admin
from django.urls import reverse


def get_model_from_app_list(app_list, app_label, model_name):
    """Знайти модель в app_list"""
    for app in app_list:
        if app['app_label'] == app_label:
            for model in app.get('models', []):
                if model['object_name'] == model_name:
                    return model
    return None


def custom_get_app_list(self, request):
    """
    Перегрупувати моделі адмінки з чіткою ієрархією:
    Кожна сторінка = окрема вкладка, секції = підпункти
    """
    # Отримати стандартний app_list
    original_app_list = original_get_app_list(self, request)
    
    # Створити нову структуру
    new_app_list = [
        {
            'name': '📋 Наповнення Сайту',
            'app_label': 'content_management',
            'app_url': '#',
            'has_module_perms': True,
            'models': [
                # === 🏠 Головна ===
                {'name': '🏠 Головна', 'admin_url': '#', 'view_only': True, 'object_name': 'HomeHeader'},
                get_model_from_app_list(original_app_list, 'cms', 'HeroSlide'),
                get_model_from_app_list(original_app_list, 'cms', 'FeaturedCourseHome'),
                get_model_from_app_list(original_app_list, 'cms', 'MentorCoachingSVG'),
                get_model_from_app_list(original_app_list, 'cms', 'ExpertCard'),
                
                # === 📖 Про нас ===
                {'name': '📖 Про нас', 'admin_url': '#', 'view_only': True, 'object_name': 'AboutHeader'},
                get_model_from_app_list(original_app_list, 'cms', 'AboutHero'),
                get_model_from_app_list(original_app_list, 'cms', 'AboutSection2'),
                get_model_from_app_list(original_app_list, 'cms', 'AboutSection3'),
                get_model_from_app_list(original_app_list, 'cms', 'AboutSection4'),
                
                # === 🎓 Хаб знань ===
                {'name': '🎓 Хаб знань', 'admin_url': '#', 'view_only': True, 'object_name': 'HubHeader'},
                get_model_from_app_list(original_app_list, 'cms', 'HubHero'),
                get_model_from_app_list(original_app_list, 'cms', 'FeaturedCourseHub'),
                
                # === 🎉 Івенти ===
                {'name': '🎉 Івенти', 'admin_url': '#', 'view_only': True, 'object_name': 'EventsHeader'},
                get_model_from_app_list(original_app_list, 'cms', 'EventGridCell'),
                
                # === 💼 Ментор-коучинг ===
                {'name': '💼 Ментор-коучинг', 'admin_url': '#', 'view_only': True, 'object_name': 'MentorHeader'},
                get_model_from_app_list(original_app_list, 'cms', 'MentorHero'),
                get_model_from_app_list(original_app_list, 'cms', 'MentorSection1Image'),
                get_model_from_app_list(original_app_list, 'cms', 'MentorSection2'),
                get_model_from_app_list(original_app_list, 'cms', 'MentorSection3'),
                get_model_from_app_list(original_app_list, 'cms', 'MentorSection4'),
                
                # === 💳 Підписка ===
                {'name': '💳 Підписка', 'admin_url': '#', 'view_only': True, 'object_name': 'SubscriptionHeader'},
                get_model_from_app_list(original_app_list, 'subscriptions', 'SubscriptionPlan'),
                get_model_from_app_list(original_app_list, 'subscriptions', 'Subscription'),
                
                # === ➕ Додати курс ===
                {'name': '➕ Додати курс', 'admin_url': '#', 'view_only': True, 'object_name': 'AddCourseHeader'},
                get_model_from_app_list(original_app_list, 'content', 'Course'),
                
                # === ➕ Додати івент ===
                {'name': '➕ Додати івент', 'admin_url': '#', 'view_only': True, 'object_name': 'AddEventHeader'},
                get_model_from_app_list(original_app_list, 'events', 'Event'),
            ]
        },
        {
            'name': '🔧 Управління',
            'app_label': 'management',
            'app_url': '#',
            'has_module_perms': True,
            'models': [
                # === 📊 Pixel ===
                {'name': '📊 Pixel', 'admin_url': '#', 'view_only': True, 'object_name': 'PixelHeader'},
                get_model_from_app_list(original_app_list, 'cms', 'TrackingPixel'),
                
                # === 🤖 AI ===
                {'name': '🤖 AI', 'admin_url': '#', 'view_only': True, 'object_name': 'AIHeader'},
                get_model_from_app_list(original_app_list, 'ai', 'AIConfiguration'),
                get_model_from_app_list(original_app_list, 'ai', 'AIKnowledgeDocument'),
                
                # === 📈 Статистика ===
                {'name': '📈 Статистика', 'admin_url': '#', 'view_only': True, 'object_name': 'StatsHeader'},
                get_model_from_app_list(original_app_list, 'analytics', 'DashboardStats'),
                
                # === 📥 Заявки з лендінгу ===
                {'name': '📥 Заявки з лендінгу', 'admin_url': '#', 'view_only': True, 'object_name': 'LeadsHeader'},
                get_model_from_app_list(original_app_list, 'landing', 'LeadSubmission'),
            ]
        },
        # Додати інші застосунки (Users, Auth тощо)
        *[app for app in original_app_list if app['app_label'] in ['auth', 'accounts']]
    ]
    
    # Відфільтрувати None (моделі що не знайдено)
    for app in new_app_list:
        app['models'] = [m for m in app.get('models', []) if m is not None]
    
    return new_app_list


# Зберегти оригінальний метод
original_get_app_list = admin.AdminSite.get_app_list

# Застосувати monkey patch
admin.AdminSite.get_app_list = custom_get_app_list

