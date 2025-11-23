"""
HTMX views for content (hub)
Separate HTMX view for NAVIGATION (не конфліктує з фільтрами!)
"""
from apps.content.views import CourseListView


class HTMXCourseListView(CourseListView):
    """
    ОКРЕМИЙ HTMX view для NAVIGATION (не для фільтрів!)
    Завжди повертає ПОВНУ сторінку hub
    
    Існуючий CourseListView використовується для фільтрів через /hub/
    Цей view використовується тільки для navigation через /htmx/hub/
    """
    template_name = 'htmx/hub/course_list_content.html'
    
    def render_to_response(self, context, **response_kwargs):
        # НЕ перевіряємо HX-Request - завжди повна сторінка
        # Викликаємо render_to_response батьківського класу ListView,
        # пропускаючи логіку CourseListView з перевіркою HX-Request
        from django.views.generic import ListView
        return ListView.render_to_response(self, context, **response_kwargs)

