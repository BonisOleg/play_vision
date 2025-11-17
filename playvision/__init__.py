# Celery не використовується (NO Redis on Render starter)
pass

# Застосувати кастомну структуру адмінки
try:
    from . import admin_structure
except ImportError:
    pass
