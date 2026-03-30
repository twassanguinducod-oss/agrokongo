"""
Django settings for agrokongo project.
AgroKongo - Marketplace Agrícola para Angola 🇦🇴
Production-Ready Configuration
"""
import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
# ===========================================
# 1. BASE CONFIGURATIONS
# ===========================================
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

# ✅ CONFIGURAÇÃO DE MEDIA (UPLOAD DE FICHEIROS)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Limitar tamanho de upload (5MB)
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    'agrokongo.ao',
    'www.agrokongo.ao',
]

# ===========================================
# 2. INSTALLED APPS
# ===========================================

INSTALLED_APPS = [
    # Django Contrib
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'drf_spectacular',

    # Apps do AgroKongo
    'locations',
    'accounts',
    'marketplace',
    'core',
]

# ===========================================
# 3. MIDDLEWARE
# ===========================================

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'agrokongo.urls'

# ===========================================
# 4. TEMPLATES
# ===========================================

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
            ],
        },
    },
]

WSGI_APPLICATION = 'agrokongo.wsgi.application'

# ===========================================
# 5. DATABASE (PostgreSQL)
# ===========================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 10,
        },
    }
}

# ===========================================
# 6. PASSWORD VALIDATION
# ===========================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ===========================================
# 7. INTERNATIONALIZATION
# ===========================================

LANGUAGE_CODE = 'pt-ao'
TIME_ZONE = 'Africa/Luanda'
USE_I18N = True
USE_TZ = True

# ===========================================
# 8. STATIC & MEDIA FILES
# ===========================================

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ===========================================
# 9. CUSTOM USER MODEL
# ===========================================

AUTH_USER_MODEL = 'accounts.Usuario'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===========================================
# 10. JWT CONFIGURATION (SimpleJWT)
# ===========================================

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY or 'fallback-para-desenvolvimento-apenas',
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
}

# ===========================================
# 11. REST FRAMEWORK CONFIGURATION
# ===========================================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated', # 🛡️ SEGURANÇA: Alterado de AllowAny
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
    },
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# ===========================================
# 12. CORS CONFIGURATION
# ===========================================

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'https://agrokongo.ao',
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# ===========================================
# 13. CSRF CONFIGURATION
# ===========================================

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'https://agrokongo.ao',
]

# ===========================================
# 14. CACHE CONFIGURATION (✅ CORRETA)
# ===========================================

# Opção A: Backend Nativo do Django (Recomendado para Django 4+)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),
        'TIMEOUT': 300,
        # ✅ SEM 'OPTIONS' com CLIENT_CLASS para backend nativo
    }
}

# Opção B: Se precisares de django-redis (descomenta apenas se instalares django-redis)
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',  # ← Requer: pip install django-redis
#         'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),
#         'TIMEOUT': 300,
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',  # ← Só funciona com django_redis
#             'SOCKET_CONNECT_TIMEOUT': 5,
#             'SOCKET_TIMEOUT': 5,
#         }
#     }
# }

# ===========================================
# 15. CELERY CONFIGURATION
# ===========================================

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Africa/Luanda'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 300

# ===========================================
# 16. SPECTACULAR (Swagger/OpenAPI)
# ===========================================

SPECTACULAR_SETTINGS = {
    'TITLE': 'AgroKongo API',
    'DESCRIPTION': 'Marketplace Agrícola para Angola',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,

    # ✅ RESOLVER ENUM COLLISIONS
    'ENUM_NAME_OVERRIDES': {
        # Accounts
        'UsuarioTipoEnum': 'accounts.models.Usuario.TIPO_CHOICES',

        # Marketplace - Safra
        'SafraStatusEnum': 'marketplace.models.Safra.STATUS_CHOICES',

        # Marketplace - Reserva
        'ReservaStatusEnum': 'marketplace.models.Reserva.STATUS_CHOICES',

        # Marketplace - Pagamento
        'PagamentoStatusEnum': 'marketplace.models.Pagamento.STATUS_CHOICES',
        'PagamentoMetodoEnum': 'marketplace.models.Pagamento.METODO_CHOICES',

        # Core - Notificacao
        'NotificacaoTipoEnum': 'core.models.Notificacao.TIPO_CHOICES',

        # Core - Mensagem
        'MensagemStatusEnum': 'core.models.Mensagem.STATUS_CHOICES',

        # Core - LogAuditoria
        'LogAuditoriaAcaoEnum': 'core.models.LogAuditoria.ACAO_CHOICES',
    },

    # ✅ NOMES MAIS CLAROS
    'COMPONENT_SPLIT_REQUEST': True,
    'CONVERT_PATH_PARAM_WITH_DOUBLE_BRACKET': True,

    # ✅ PREVENIR WARNINGS
    'ENUM_ADD_EXPLICIT_BLANK_NULL_CHOICE': False,
}

# ===========================================
# 17. EMAIL CONFIGURATION
# ===========================================

EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend' if DEBUG else 'django.core.mail.backends.smtp.EmailBackend'
)

EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'AgroKongo <noreply@agrokongo.ao>')

# ===========================================
# 18. LOGGING CONFIGURATION
# ===========================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'agrokongo.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose',
            'level': 'INFO',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Criar pasta de logs
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# ===========================================
# 19. SECURITY SETTINGS (Produção)
# ===========================================

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# ===========================================
# 20. SESSION CONFIGURATION
# ===========================================

SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_NAME = 'agrokongo_sessionid'
SESSION_COOKIE_AGE = 1209600
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# ===========================================
# 21. BUSINESS LOGIC CONSTANTS
# ===========================================

from decimal import Decimal

PLATAFORMA_COMISSAO_PERCENTUAL = Decimal('0.05')
PRAZO_ENTREGA_PADRAO_DIAS = 3
TEMPO_LIMITE_PAGAMENTO_HORAS = 24
RATING_MINIMO_PRODUTOR = Decimal('3.00')

# ===========================================
# 22. LOCAL SETTINGS (Opcional)
# ===========================================

try:
    from .local_settings import *
except ImportError:
    pass