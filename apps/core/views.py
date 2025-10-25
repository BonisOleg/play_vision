from django.views.generic import TemplateView, FormView, View
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.contrib import messages
from django import forms
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponse, FileResponse
import os


class ContactForm(forms.Form):
    """Contact form"""
    name = forms.CharField(max_length=100, label='Ім\'я')
    email = forms.EmailField(label='Email')
    phone = forms.CharField(max_length=20, required=False, label='Телефон')
    subject = forms.CharField(max_length=200, label='Тема')
    message = forms.CharField(widget=forms.Textarea, label='Повідомлення')


class HomeView(TemplateView):
    """Home page view"""
    template_name = 'pages/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Featured courses для каруселі (6 курсів)
        from apps.content.models import Course
        context['featured_courses'] = Course.objects.filter(
            is_published=True,
            is_featured=True
        ).select_related('category').prefetch_related('tags')[:6]
        
        # CMS контент
        from apps.cms.models import HeroSlide, PageSection, ExpertCard, HexagonItem
        
        context['cms_hero_slides'] = HeroSlide.objects.filter(is_active=True)
        context['cms_sections'] = PageSection.objects.filter(
            page='home',
            is_active=True
        ).prefetch_related('blocks')
        context['cms_experts'] = ExpertCard.objects.filter(
            is_active=True,
            show_on_homepage=True
        )
        context['cms_hexagons'] = HexagonItem.objects.filter(is_active=True)
        
        return context


class MentoringView(TemplateView):
    """Ментор-коучинг сторінка"""
    template_name = 'pages/mentoring.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class AboutView(TemplateView):
    """About page view - Про нас"""
    template_name = 'pages/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        from apps.cms.models import PageSection, ExpertCard
        
        # CMS секції для сторінки "Про нас"
        context['cms_sections'] = PageSection.objects.filter(
            page='about',
            is_active=True
        ).prefetch_related('blocks')
        
        # Команда/Експерти для блоку "Наша команда"
        context['cms_experts'] = ExpertCard.objects.filter(
            is_active=True,
            show_on_homepage=False  # Показуємо тільки тих, хто не на головній
        )
        
        return context


class ComingSoonView(TemplateView):
    """Coming soon page for future features"""
    template_name = 'pages/coming_soon.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.request.GET.get('page', 'feature')
        
        # Content for different coming soon pages
        coming_soon_content = {
            'mentoring': {
                'title': 'Ментор-коучинг',
                'subtitle': 'Персональний розвиток з експертами',
                'description': 'Незабаром ви зможете отримати персональні консультації від топових тренерів та аналітиків.',
                'features': [
                    'Індивідуальні сесії з тренерами',
                    'Аналіз ваших матчів',
                    'Персональний план розвитку',
                    'Доступ до закритої спільноти'
                ]
            },
            'subscription': {
                'title': 'Підписка Pro-Vision',
                'subtitle': 'Безлімітний доступ до знань',
                'description': 'Отримайте доступ до всіх курсів, ексклюзивних матеріалів та спеціальних івентів.',
                'features': [
                    'Доступ до всіх курсів',
                    'Пріоритетна реєстрація на івенти',
                    'Ексклюзивні матеріали',
                    'Закрита спільнота підписників'
                ]
            }
        }
        
        context['content'] = coming_soon_content.get(page, {
            'title': 'Незабаром',
            'subtitle': 'Працюємо над новими можливостями',
            'description': 'Ця функція знаходиться в розробці. Слідкуйте за оновленнями!',
            'features': []
        })
        
        return context


class ContactView(FormView):
    """Contact page view"""
    template_name = 'pages/contacts.html'
    form_class = ContactForm
    success_url = reverse_lazy('core:contacts')
    
    def form_valid(self, form):
        # Send email
        subject = f"Contact form: {form.cleaned_data['subject']}"
        message = f"""
        Name: {form.cleaned_data['name']}
        Email: {form.cleaned_data['email']}
        Phone: {form.cleaned_data.get('phone', 'Not provided')}
        
        Message:
        {form.cleaned_data['message']}
        """
        
        try:
            send_mail(
                subject,
                message,
                form.cleaned_data['email'],
                ['support@playvision.com'],
                fail_silently=False,
            )
            messages.success(self.request, 'Ваше повідомлення успішно відправлено!')
        except Exception as e:
            messages.error(self.request, 'Помилка відправки повідомлення. Спробуйте пізніше.')
        
        return super().form_valid(form)


class LegalPageView(TemplateView):
    """Legal pages view"""
    template_name = 'pages/legal.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug')
        
        # Legal page content would come from database or files
        legal_pages = {
            'privacy': {
                'title': 'Політика приватності',
                'content': 'Зміст політики приватності...'
            },
            'terms': {
                'title': 'Умови використання',
                'content': 'Зміст умов використання...'
            },
            'cookies': {
                'title': 'Політика cookies',
                'content': 'Зміст політики cookies...'
            }
        }
        
        context['page'] = legal_pages.get(slug, {})
        return context


class PricingView(TemplateView):
    """Pricing page view"""
    template_name = 'subscriptions/pricing.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get subscription plans
        from apps.subscriptions.models import Plan
        context['plans'] = Plan.objects.filter(is_active=True).order_by('duration_months')
        
        # Get popular courses for comparison
        from apps.content.models import Course
        context['popular_courses'] = Course.objects.filter(
            is_published=True,
            is_featured=True
        ).order_by('-view_count')[:5]
        
        return context


class SearchView(TemplateView):
    """Global search view"""
    template_name = 'pages/search.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        
        if query:
            context['query'] = query
            context['results'] = self.perform_search(query)
        else:
            context['query'] = ''
            context['results'] = {'courses': [], 'events': [], 'total': 0}
        
        return context
    
    def perform_search(self, query):
        """Perform search across different content types"""
        from apps.content.models import Course
        from apps.events.models import Event
        from django.db.models import Q
        from django.utils import timezone
        
        # Search courses
        courses = Course.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__name__icontains=query),
            is_published=True
        ).distinct()[:10]
        
        # Search events (with error handling)
        try:
            events = Event.objects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(speakers__first_name__icontains=query) |
                Q(speakers__last_name__icontains=query),
                status='published',
                start_datetime__gte=timezone.now()
            ).distinct()[:10]
        except Exception:
            events = Event.objects.none()
        
        return {
            'courses': courses,
            'events': events,
            'total': courses.count() + events.count()
        }


class RobotsView(TemplateView):
    """Robots.txt view"""
    template_name = 'robots.txt'
    content_type = 'text/plain'


class SitemapView(TemplateView):
    """Sitemap view"""
    template_name = 'sitemap.xml'
    content_type = 'application/xml'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all published content for sitemap
        from apps.content.models import Course
        from apps.events.models import Event
        from django.utils import timezone
        
        context['courses'] = Course.objects.filter(is_published=True)
        try:
            context['events'] = Event.objects.filter(status='published')
        except Exception:
            context['events'] = Event.objects.none()
        context['last_modified'] = timezone.now()
        
        return context


class HealthCheckView(TemplateView):
    """Health check for monitoring"""
    
    def get(self, request, *args, **kwargs):
        from django.http import JsonResponse
        from django.db import connection
        
        # Check database connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                db_status = "ok"
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        # Check cache (if configured)
        cache_status = "ok"
        try:
            from django.core.cache import cache
            cache.set('health_check', 'ok', 10)
            if cache.get('health_check') != 'ok':
                cache_status = "error"
        except Exception as e:
            cache_status = f"error: {str(e)}"
        
        status = {
            'status': 'ok' if db_status == 'ok' and cache_status == 'ok' else 'error',
            'database': db_status,
            'cache': cache_status,
            'timestamp': timezone.now().isoformat()
        }
        
        status_code = 200 if status['status'] == 'ok' else 503
        return JsonResponse(status, status=status_code)


class TemplateDebugView(TemplateView):
    """Debug view to test template processing"""
    template_name = 'debug_test.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'debug': settings.DEBUG,
            'test_datetime': timezone.now(),
        })
        return context


class PWAOfflineView(TemplateView):
    """PWA Offline fallback page"""
    template_name = 'pwa/offline.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_pwa'] = True
        return context


class PWAInstallView(TemplateView):
    """PWA Installation instructions page"""
    template_name = 'pwa/install.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Визначити тип пристрою
        user_agent = self.request.META.get('HTTP_USER_AGENT', '').lower()
        
        if 'iphone' in user_agent or 'ipad' in user_agent:
            context['device_type'] = 'ios'
        elif 'android' in user_agent:
            context['device_type'] = 'android'
        else:
            context['device_type'] = 'desktop'
        
        context['is_pwa'] = True
        return context


class PDFBackgroundsDemoView(TemplateView):
    """Demo page for PDF backgrounds"""
    template_name = 'pages/pdf-backgrounds-demo.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        import json
        from pathlib import Path
        
        # Читаємо маніфест з інформацією про зображення
        manifest_path = Path(settings.BASE_DIR) / 'static' / 'images' / 'pdf-backgrounds' / 'manifest.json'
        if manifest_path.exists():
            with open(manifest_path, 'r', encoding='utf-8') as f:
                context['backgrounds_manifest'] = json.load(f)
        else:
            context['backgrounds_manifest'] = {}
        
        return context


class ServiceWorkerView(View):
    """Serve Service Worker from root path"""
    
    def get(self, request, *args, **kwargs):
        """Serve sw.js file with proper headers"""
        sw_path = os.path.join(settings.BASE_DIR, 'sw.js')
        
        if os.path.exists(sw_path):
            response = FileResponse(
                open(sw_path, 'rb'),
                content_type='application/javascript'
            )
            # Add Service Worker specific headers
            response['Cache-Control'] = 'no-cache'
            response['Service-Worker-Allowed'] = '/'
            return response
        
        # Fallback if file not found
        return HttpResponse(
            'Service Worker not found',
            status=404,
            content_type='text/plain'
        )