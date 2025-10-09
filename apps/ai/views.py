from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
import json
from .models import AIQuery, KnowledgeBase, AIConfiguration
from .services import AIAgentService, KnowledgeBaseLoader


class AIChatView(TemplateView):
    """Головна сторінка AI чату"""
    template_name = 'ai/chat.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Перевірити чи увімкнений AI
        config = AIConfiguration.objects.first()
        context['ai_enabled'] = config.is_enabled if config else False
        context['maintenance_message'] = config.maintenance_message if config else ''
        
        # Рекомендовані запитання
        ai_service = AIAgentService()
        access_level = ai_service._get_user_access_level(self.request.user)
        context['suggested_questions'] = ai_service.get_suggested_questions(access_level)
        
        # Історія для авторизованих користувачів
        if self.request.user.is_authenticated:
            context['recent_queries'] = AIQuery.objects.filter(
                user=self.request.user
            ).order_by('-created_at')[:5]
        
        return context


class AIAskAPIView(View):
    """API endpoint для запитів до AI"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            query = data.get('query', '').strip()
            
            if not query:
                return JsonResponse({
                    'success': False,
                    'message': 'Порожній запит'
                })
            
            if len(query) > 500:
                return JsonResponse({
                    'success': False,
                    'message': 'Запит занадто довгий (максимум 500 символів)'
                })
            
            # Обробка через AI сервіс
            ai_service = AIAgentService()
            session_id = request.session.session_key or request.session.create()
            
            # Трекінг кількості запитів в сесії
            from django.core.cache import cache
            cache_key = f"ai_queries_{session_id}"
            queries_count = cache.get(cache_key, 0) + 1
            cache.set(cache_key, queries_count, timeout=3600)  # 1 година
            
            result = ai_service.process_query(
                query=query,
                user=request.user if request.user.is_authenticated else None,
                session_id=session_id,
                queries_count=queries_count
            )
            
            return JsonResponse(result)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Невірний формат даних'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': 'Помилка сервера',
                'error': str(e) if settings.DEBUG else None
            })


class AIWidgetFAQView(TemplateView):
    """AI віджет для FAQ сторінки"""
    template_name = 'ai/widgets/faq_widget.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['widget_type'] = 'faq'
        context['placeholder'] = 'Запитайте про Play Vision...'
        return context


class AIWidgetHubView(TemplateView):
    """AI віджет для Хабу знань"""
    template_name = 'ai/widgets/hub_widget.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['widget_type'] = 'hub'
        context['placeholder'] = 'Як обрати курс? Що вивчати далі?'
        return context


class AIWidgetCabinetView(LoginRequiredMixin, TemplateView):
    """AI віджет для особистого кабінету"""
    template_name = 'ai/widgets/cabinet_widget.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['widget_type'] = 'cabinet'
        context['placeholder'] = 'Питання про підписку, прогрес, налаштування...'
        return context


class AIRateResponseView(View):
    """Оцінка відповіді AI"""
    
    def post(self, request, query_id):
        try:
            data = json.loads(request.body)
            rating = int(data.get('rating', 0))
            
            if not 1 <= rating <= 5:
                return JsonResponse({
                    'success': False,
                    'message': 'Оцінка повинна бути від 1 до 5'
                })
            
            # Знайти запит
            query_filter = {'id': query_id}
            if request.user.is_authenticated:
                query_filter['user'] = request.user
            else:
                query_filter['session_id'] = request.session.session_key
            
            query = get_object_or_404(AIQuery, **query_filter)
            query.user_rating = rating
            query.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Дякуємо за оцінку!'
            })
            
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({
                'success': False,
                'message': 'Невірні дані'
            })


class AIFeedbackView(View):
    """Відгук на відповідь AI"""
    
    def post(self, request, query_id):
        try:
            data = json.loads(request.body)
            feedback = data.get('feedback', '').strip()
            
            if not feedback:
                return JsonResponse({
                    'success': False,
                    'message': 'Порожній відгук'
                })
            
            # Знайти запит
            query_filter = {'id': query_id}
            if request.user.is_authenticated:
                query_filter['user'] = request.user
            else:
                query_filter['session_id'] = request.session.session_key
            
            query = get_object_or_404(AIQuery, **query_filter)
            query.user_feedback = feedback[:500]  # Обмежити довжину
            query.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Дякуємо за відгук!'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Невірний формат даних'
            })


class AISuggestionsAPIView(View):
    """API для отримання рекомендованих запитань"""
    
    def get(self, request):
        ai_service = AIAgentService()
        access_level = ai_service._get_user_access_level(request.user)
        suggestions = ai_service.get_suggested_questions(access_level)
        
        return JsonResponse({
            'suggestions': suggestions,
            'access_level': access_level
        })


@method_decorator(staff_member_required, name='dispatch')
class LoadKnowledgeBaseView(View):
    """Завантаження бази знань з файлів (тільки для адміністраторів)"""
    
    def post(self, request):
        loader = KnowledgeBaseLoader()
        
        # Директорія з базою знань
        knowledge_dir = settings.BASE_DIR / 'ai_knowledge_base'
        
        if not knowledge_dir.exists():
            return JsonResponse({
                'success': False,
                'message': f'Директорія {knowledge_dir} не існує'
            })
        
        try:
            loaded_count = loader.load_from_directory(str(knowledge_dir))
            
            return JsonResponse({
                'success': True,
                'message': f'Завантажено {loaded_count} документів в базу знань',
                'loaded_count': loaded_count
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Помилка завантаження: {str(e)}'
            })


@method_decorator(staff_member_required, name='dispatch')
class IndexCourseView(View):
    """Індексування курсу в базу знань"""
    
    def post(self, request, course_id):
        loader = KnowledgeBaseLoader()
        success = loader.index_course_content(course_id)
        
        if success:
            return JsonResponse({
                'success': True,
                'message': f'Курс #{course_id} проіндексований'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Помилка індексування курсу'
            })


@method_decorator(staff_member_required, name='dispatch')
class KnowledgeStatsView(View):
    """Статистика бази знань"""
    
    def get(self, request):
        stats = {
            'total_entries': KnowledgeBase.objects.count(),
            'indexed_entries': KnowledgeBase.objects.filter(is_indexed=True).count(),
            'by_access_level': {},
            'by_content_type': {},
            'total_queries': AIQuery.objects.count(),
            'avg_rating': 0
        }
        
        # Статистика по рівнях доступу
        for level, _ in KnowledgeBase._meta.get_field('access_level').choices:
            count = KnowledgeBase.objects.filter(access_level=level).count()
            stats['by_access_level'][level] = count
        
        # Статистика по типах контенту
        for content_type, _ in KnowledgeBase._meta.get_field('content_type').choices:
            count = KnowledgeBase.objects.filter(content_type=content_type).count()
            stats['by_content_type'][content_type] = count
        
        # Середня оцінка
        rated_queries = AIQuery.objects.filter(user_rating__isnull=False)
        if rated_queries.exists():
            total_rating = sum(q.user_rating for q in rated_queries)
            stats['avg_rating'] = round(total_rating / rated_queries.count(), 2)
        
        return JsonResponse(stats)
