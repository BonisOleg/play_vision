"""
Django settings for playvision project.
Auto-selects between development and production settings based on environment.
"""
import os

# Determine which settings to use
env = os.environ.get('DJANGO_ENV', 'development')

if env == 'production':
    from .settings.production import *
else:
    from .settings.development import *

# Make settings available at module level
import sys
current_module = sys.modules[__name__]

# Import the appropriate settings module
if env == 'production':
    from .settings import production as settings_module
else:
    from .settings import development as settings_module

# Copy all settings to current module
for setting in dir(settings_module):
    if setting.isupper():
        setattr(current_module, setting, getattr(settings_module, setting))