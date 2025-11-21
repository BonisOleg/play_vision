"""
Core views - Admin dashboard and public pages
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from django.http import HttpResponse
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


# Public pages
class HomeView(TemplateView):
    """Home page"""
    template_name = 'pages/home.html'


class AboutView(TemplateView):
    """About page"""
    template_name = 'pages/about.html'


class MentoringView(TemplateView):
    """Mentoring page"""
    template_name = 'pages/mentoring.html'


class ContactView(TemplateView):
    """Contact page"""
    template_name = 'pages/contact.html'


class SearchView(TemplateView):
    """Search page"""
    template_name = 'pages/search.html'


class ComingSoonView(TemplateView):
    """Coming soon page"""
    template_name = 'pages/coming_soon.html'


class PDFBackgroundsDemoView(TemplateView):
    """PDF backgrounds demo"""
    template_name = 'pages/pdf_backgrounds_demo.html'


class PWAOfflineView(TemplateView):
    """PWA offline page"""
    template_name = 'pwa/offline.html'


class PWAInstallView(TemplateView):
    """PWA install page"""
    template_name = 'pwa/install.html'


class LegalPageView(TemplateView):
    """Legal pages - privacy, terms, copyright"""
    
    def get_template_names(self):
        slug = self.kwargs.get('slug', 'privacy')
        return [f'legal/{slug}.html']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get('slug', 'privacy')
        
        # SEO metadata for different legal pages
        meta_data = {
            'privacy': {
                'title': 'Політика конфіденційності',
                'description': 'Політика конфіденційності компанії Play Vision'
            },
            'terms': {
                'title': 'Договір оферти',
                'description': 'Публічний договір оферти компанії Play Vision'
            },
            'copyright': {
                'title': 'Права інтелектуальної власності',
                'description': 'Інформація про захист прав інтелектуальної власності'
            }
        }
        
        context['meta'] = meta_data.get(slug, meta_data['privacy'])
        return context


class RobotsView(TemplateView):
    """Robots.txt"""
    template_name = 'robots.txt'
    content_type = 'text/plain'


class SitemapView(TemplateView):
    """Sitemap.xml"""
    template_name = 'sitemap.xml'
    content_type = 'application/xml'


class HealthCheckView(TemplateView):
    """Health check endpoint"""
    def get(self, request, *args, **kwargs):
        return HttpResponse('OK', content_type='text/plain')


class ServiceWorkerView(TemplateView):
    """Service worker"""
    template_name = 'sw.js'
    content_type = 'application/javascript'


@staff_member_required
def admin_dashboard(request):
    """
    Custom admin dashboard with statistics
    
    Shows:
    - User metrics
    - Revenue
    - Session duration
    - Course views
    
    Supports date range filter: today, week, month
    """
    # Get period from query params
    period = request.GET.get('period', 'week')
    
    # Calculate date range
    now = timezone.now()
    if period == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'month':
        start_date = now - timedelta(days=30)
    else:  # week (default)
        start_date = now - timedelta(days=7)
    
    # Get statistics
    from apps.accounts.models import User
    from apps.payments.models import Payment
    from apps.analytics.models import UserSession, DashboardStats
    from apps.content.models import Course
    
    # User stats
    total_users = User.objects.count()
    new_users = User.objects.filter(created_at__gte=start_date).count()
    
    # Revenue stats
    revenue_data = Payment.objects.filter(
        status='completed',
        completed_at__gte=start_date
    ).aggregate(
        total=Sum('amount'),
        count=Count('id')
    )
    period_revenue = revenue_data['total'] or 0
    payment_count = revenue_data['count'] or 0
    
    # Total revenue (all time)
    total_revenue = Payment.objects.filter(
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Session stats
    sessions = UserSession.objects.filter(started_at__gte=start_date)
    session_stats = sessions.aggregate(
        avg_duration=Avg('duration_seconds'),
        total_time=Sum('duration_seconds'),
        count=Count('id')
    )
    
    avg_session_minutes = (session_stats['avg_duration'] or 0) / 60
    total_time_hours = (session_stats['total_time'] or 0) / 3600
    session_count = session_stats['count']
    
    # Course views - top 10
    top_courses = Course.objects.filter(
        is_published=True
    ).order_by('-view_count')[:10].values(
        'id', 'title', 'view_count', 'enrollment_count'
    )
    
    # Latest dashboard stats (for historical comparison)
    latest_stats = DashboardStats.objects.order_by('-date').first()
    
    context = {
        # Filters
        'period': period,
        'start_date': start_date,
        'period_display': {
            'today': 'Today',
            'week': 'Last 7 Days',
            'month': 'Last 30 Days'
        }.get(period, 'Last 7 Days'),
        
        # User metrics
        'total_users': total_users,
        'new_users': new_users,
        
        # Revenue metrics
        'total_revenue': total_revenue,
        'period_revenue': period_revenue,
        'payment_count': payment_count,
        
        # Session metrics
        'avg_session_minutes': round(avg_session_minutes, 1),
        'total_time_hours': round(total_time_hours, 1),
        'session_count': session_count,
        
        # Course data
        'top_courses': list(top_courses),
        
        # Latest stats
        'latest_stats': latest_stats,
    }
    
    return render(request, 'admin/dashboard.html', context)
