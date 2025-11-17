"""
Production settings for Play Vision
Optimized for Render.com deployment
"""
import dj_database_url
import os
from .base import *

# Security
DEBUG = False

# Allowed hosts configuration
ALLOWED_HOSTS = []
hosts_env = config('ALLOWED_HOSTS', default='')
if hosts_env:
    ALLOWED_HOSTS.extend(hosts_env.split(','))

# Add Render.com internal IPs
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Add common Render patterns
ALLOWED_HOSTS.extend([
    '*.onrender.com',
    'playvision.onrender.com'
])

# Database - Use DATABASE_URL from Render
DATABASES['default'] = dj_database_url.config(
    conn_max_age=600,
    conn_health_checks=True,
)

# Security headers - Enhanced for production
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Cookies security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# CSRF trusted origins for Render
csrf_origins_env = config('CSRF_TRUSTED_ORIGINS', default='')
CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'https://playvision.onrender.com'
]
if csrf_origins_env:
    CSRF_TRUSTED_ORIGINS.extend(csrf_origins_env.split(','))

# Static files - WhiteNoise configuration
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Temporarily disable compression for debugging staticfiles issues
WHITENOISE_COMPRESS_OFFLINE = False
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = ['*']

# Sentry Integration
SENTRY_DSN = config('SENTRY_DSN', default='')

if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
            RedisIntegration(),
        ],
        traces_sample_rate=0.1,  # 10% performance monitoring
        profiles_sample_rate=0.1,  # 10% profiling
        send_default_pii=False,  # GDPR compliance - no PII
        environment=config('ENV', default='production'),
        before_send=lambda event, hint: event if event.get('level') != 'debug' else None,
    )

# Structured JSON Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d',
        },
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'performance': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Email - Gmail SMTP з App Password
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)

# Cloudinary для зображень (обов'язково для продакшену)
if config('CLOUDINARY_URL', default=''):
    # Cloudinary налаштовано через CLOUDINARY_URL
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
    
    cloudinary.config(
        cloud_name=config('CLOUDINARY_CLOUD_NAME', default=''),
        api_key=config('CLOUDINARY_API_KEY', default=''),
        api_secret=config('CLOUDINARY_API_SECRET', default=''),
        secure=True
    )
    
    # Використовувати Cloudinary для MEDIA файлів
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    MEDIA_URL = f"https://res.cloudinary.com/{config('CLOUDINARY_CLOUD_NAME')}/image/upload/"
else:
    # Fallback якщо Cloudinary не налаштований
    print("WARNING: Cloudinary not configured! Using local storage.")
    MEDIA_ROOT = BASE_DIR / 'mediafiles'
    MEDIA_URL = '/media/'

# VAPID ключі для push notifications
VAPID_PRIVATE_KEY = 'MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgjr19PQPYfjKqpEr6X7783aTxE-CIHkCfFHN1ePvTr66hRANCAAQDScS1jLjPfzr_ieuChn__WVxHE2oLHNhnWr4NoSDmEDuK9dEEpUy7gIRJB7CBIkVXmKXozDRa5lin1tQWp6sh'
VAPID_PUBLIC_KEY = 'BANJxLWMuM9_Ov-J64KGf_9ZXEcTagsc2Gdavg2hIOYQO4r10QSlTLuAhEkHsIEiRVeYpejMNFrmWKfW1BanqyE'
VAPID_CLAIMS = {'sub': 'mailto:admin@playvision.com'}

# Logging for production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
        'apps': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}