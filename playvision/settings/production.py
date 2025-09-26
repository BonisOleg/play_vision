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
CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'https://playvision.onrender.com'
]

# Static files - WhiteNoise configuration
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Temporarily disable compression for debugging staticfiles issues
WHITENOISE_COMPRESS_OFFLINE = False
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = ['*']

# Email - временно используем консольный бэкенд для отладки
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'  
# TODO: Настроить нормальный SMTP после получения учетных данных

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