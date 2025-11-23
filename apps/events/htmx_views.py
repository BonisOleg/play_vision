"""
HTMX views for events
Partial templates for navigation without full page reload
"""
from apps.events.views import EventListView


class HTMXEventListView(EventListView):
    """HTMX partial для events page"""
    template_name = 'htmx/events/event_list_content.html'

