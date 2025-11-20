"""
Base settings for Play Vision project
"""
import os
from pathlib import Path
from decouple import config

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Security
SECRET_KEY = config('SECRET_KEY', default='django-insecure-temp-key-change-in-production')
# DEBUG завжди True для розробки  
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
    'django_htmx',
    'widget_tweaks',
    'whitenoise.runserver_nostatic',
    'cloudinary_storage',
    'cloudinary',
]

LOCAL_APPS = [
    'apps.core',
    'apps.accounts',
    'apps.subscriptions',
    'apps.payments',
    'apps.content',
    'apps.cart',
    'apps.events',
    'apps.loyalty',  # Стандартизована назва
    'apps.mentoring',  # Стандартизована назва
    'apps.ai',  # Стандартизована назва
    'apps.analytics',  # Стандартизована назва
    'apps.notifications',  # Стандартизована назва
    'apps.cms',  # Стандартизована назва
    'apps.video_security',  # Стандартизована назва
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.core.services.RequestContextMiddleware',  # Request context for signals
    'playvision.middleware.CountryDetectionMiddleware',  # GeoIP detection
    'playvision.middleware.AdminRateLimitMiddleware',  # Admin security
    'playvision.middleware.PhoneRegistrationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
]

ROOT_URLCONF = 'playvision.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'apps.events.context_processors.event_categories_menu',
                'apps.cart.context_processors.cart_context',
                'apps.cms.context_processors.site_content',
            ],
        },
    },
]

WSGI_APPLICATION = 'playvision.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Cache - Simple DatabaseCache (NO REDIS!)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache_table',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Authentication
AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/account/'
LOGOUT_REDIRECT_URL = '/'

AUTHENTICATION_BACKENDS = [
    'apps.accounts.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Internationalization
LANGUAGE_CODE = 'uk'
TIME_ZONE = 'Europe/Kyiv'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files (default for development)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# STORAGES configuration (default - local storage)
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = 'Play Vision <noreply@playvision.com>'
EMAIL_SUBJECT_PREFIX = '[Play Vision] '

# Celery NOT USED

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

# GeoIP Configuration
GEOIP_PATH = BASE_DIR / 'geoip'

# Session settings - Use database backend (NO REDIS!)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 86400 * 30  # 30 days
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# CSRF settings
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# Security settings (override in production)
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5 MB

# LiqPay settings
LIQPAY_PUBLIC_KEY = config('LIQPAY_PUBLIC_KEY', default='')
LIQPAY_PRIVATE_KEY = config('LIQPAY_PRIVATE_KEY', default='')
LIQPAY_SANDBOX = config('LIQPAY_SANDBOX', default=True, cast=bool)

# Site framework
SITE_ID = 1

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Logging
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
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': config('DJANGO_LOG_LEVEL', default='INFO'),
            'propagate': False,
        },
    },
}

# WhiteNoise settings
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}

# Video Security settings (НОВІ налаштування)
VIDEO_SECURITY_ENABLED = config('VIDEO_SECURITY_ENABLED', default=False, cast=bool)
VIDEO_TOKEN_LIFETIME = config('VIDEO_TOKEN_LIFETIME', default=3600, cast=int)  # 1 година

# AWS S3 settings (опціонально для захищених відео)
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='')
AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='eu-central-1')

# Bunny.net CDN Video Streaming
BUNNY_ENABLED = config('BUNNY_ENABLED', default=True, cast=bool)
BUNNY_API_KEY = config('BUNNY_API_KEY', default='')
BUNNY_LIBRARY_ID = config('BUNNY_LIBRARY_ID', default='')
BUNNY_CDN_HOSTNAME = config('BUNNY_CDN_HOSTNAME', default='')
BUNNY_STORAGE_ZONE = config('BUNNY_STORAGE_ZONE', default='')
BUNNY_STREAM_API_URL = 'https://video.bunnycdn.com/library'
BUNNY_VIDEO_EMBED_URL = 'https://iframe.mediadelivery.net/embed'
BUNNY_TOKEN_AUTHENTICATION = config('BUNNY_TOKEN_AUTHENTICATION', default=True, cast=bool)
BUNNY_TOKEN_LIFETIME = config('BUNNY_TOKEN_LIFETIME', default=3600, cast=int)  # 1 година

# AI Assistant settings
OPENAI_API_KEY = config('OPENAI_API_KEY', default='')
ANTHROPIC_API_KEY = config('ANTHROPIC_API_KEY', default='')
AI_ENABLED = config('AI_ENABLED', default=True, cast=bool)
AI_MAX_TOKENS = config('AI_MAX_TOKENS', default=500, cast=int)
AI_TEMPERATURE = config('AI_TEMPERATURE', default=0.7, cast=float)

# PWA Settings
PWA_ENABLED = config('PWA_ENABLED', default=True, cast=bool)
PWA_APP_NAME = 'Play Vision'
PWA_APP_DESCRIPTION = 'Освітня платформа для футбольних фахівців'
PWA_APP_THEME_COLOR = '#ff6b35'
PWA_APP_BACKGROUND_COLOR = '#ffffff'
PWA_APP_START_URL = '/'
PWA_APP_SCOPE = '/'
PWA_APP_DISPLAY = 'standalone'
PWA_APP_ORIENTATION = 'portrait-primary'

# Push Notifications (VAPID) settings
VAPID_PRIVATE_KEY = config('VAPID_PRIVATE_KEY', default='')
VAPID_PUBLIC_KEY = config('VAPID_PUBLIC_KEY', default='')
VAPID_EMAIL = config('VAPID_EMAIL', default=DEFAULT_FROM_EMAIL)
