from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    # AI Chat interface
    path('chat/', views.AIChatView.as_view(), name='chat'),
    path('ask/', views.AIAskAPIView.as_view(), name='ask_api'),
    
    # Widget endpoints
    path('widget/faq/', views.AIWidgetFAQView.as_view(), name='widget_faq'),
    path('widget/hub/', views.AIWidgetHubView.as_view(), name='widget_hub'),
    path('widget/cabinet/', views.AIWidgetCabinetView.as_view(), name='widget_cabinet'),
    
    # Feedback and rating
    path('rate/<int:query_id>/', views.AIRateResponseView.as_view(), name='rate_response'),
    path('feedback/<int:query_id>/', views.AIFeedbackView.as_view(), name='feedback'),
    
    # Suggestions
    path('suggestions/', views.AISuggestionsAPIView.as_view(), name='suggestions'),
    
    # Knowledge base management (admin only)
    path('knowledge/load/', views.LoadKnowledgeBaseView.as_view(), name='load_knowledge'),
    path('knowledge/index-course/<int:course_id>/', views.IndexCourseView.as_view(), name='index_course'),
    path('knowledge/stats/', views.KnowledgeStatsView.as_view(), name='knowledge_stats'),
]
