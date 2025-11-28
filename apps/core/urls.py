from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Main pages
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('test-bunny/', views.TestBunnyView.as_view(), name='test_bunny'),
    path('mentor-coaching/', views.MentoringView.as_view(), name='mentoring'),
    path('contacts/', views.ContactView.as_view(), name='contacts'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('coming-soon/', views.ComingSoonView.as_view(), name='coming_soon'),
    path('pdf-backgrounds-demo/', views.PDFBackgroundsDemoView.as_view(), name='pdf_backgrounds_demo'),
    
    # PWA pages
    path('pwa/offline/', views.PWAOfflineView.as_view(), name='pwa_offline'),
    path('pwa/install/', views.PWAInstallView.as_view(), name='pwa_install'),
    
    # Legal pages
    path('legal/<slug:slug>/', views.LegalPageView.as_view(), name='legal'),
    
    # SEO and system
    path('robots.txt', views.RobotsView.as_view(), name='robots'),
    path('sitemap.xml', views.SitemapView.as_view(), name='sitemap'),
    path('health/', views.HealthCheckView.as_view(), name='health_check'),
    
    # PWA Service Worker
    path('sw.js', views.ServiceWorkerView.as_view(), name='service_worker'),
]
