"""
HTMX views for core pages
Partial templates for navigation without full page reload
"""
from django.views.generic import TemplateView


class HTMXHomeView(TemplateView):
    """HTMX partial для home page"""
    template_name = 'htmx/pages/home_content.html'


class HTMXAboutView(TemplateView):
    """HTMX partial для about page"""
    template_name = 'htmx/pages/about_content.html'


class HTMXMentoringView(TemplateView):
    """HTMX partial для mentoring page"""
    template_name = 'htmx/pages/mentoring_content.html'

