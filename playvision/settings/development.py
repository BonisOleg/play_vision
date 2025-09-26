"""
Development settings for Play Vision project
"""
from .base import *

# Development overrides - FORCE DEBUG ON
DEBUG = True
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']

# Development specific middleware - disable for now
# MIDDLEWARE += [
#     'playvision.middleware.NoCacheMiddleware',
#     'playvision.middleware.SecurityHeadersMiddleware', 
#     'playvision.middleware.AnalyticsMiddleware',
# ]

# Maintenance mode (disabled by default)
MAINTENANCE_MODE = False

# Database for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable cache for development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Development logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# VAPID ключі для push notifications
VAPID_PRIVATE_KEY = 'MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgjr19PQPYfjKqpEr6X7783aTxE-CIHkCfFHN1ePvTr66hRANCAAQDScS1jLjPfzr_ieuChn__WVxHE2oLHNhnWr4NoSDmEDuK9dEEpUy7gIRJB7CBIkVXmKXozDRa5lin1tQWp6sh'
VAPID_PUBLIC_KEY = 'BANJxLWMuM9_Ov-J64KGf_9ZXEcTagsc2Gdavg2hIOYQO4r10QSlTLuAhEkHsIEiRVeYpejMNFrmWKfW1BanqyE'
VAPID_CLAIMS = {'sub': 'mailto:admin@playvision.com'}
