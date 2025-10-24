"""
Django settings for playvision project.
Auto-selects between development and production settings based on environment.
"""
import os

# Determine which settings to use
env = os.environ.get('DJANGO_ENV', 'development')

if env == 'production':
    from .production import *
else:
    from .development import *

