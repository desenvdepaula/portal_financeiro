from pathlib import Path
import os
import warnings

warnings.filterwarnings(
    "ignore",
    message="pandas only supports SQLAlchemy"
)

warnings.filterwarnings(
    "ignore",
    message="NumPy was imported from a Python sub-interpreter"
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'wb71be3$x5(z8km=s64k77os5fg7)42mko0wfss1x8@ac1zbcr'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SESSION_COOKIE_NAME = "sessionid_financeiro"
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
DATABASE_ROUTERS = ['portal_financeiro.routers.AuthRouter']

ALLOWED_HOSTS = ['*']

FILE_UPLOAD_HANDLERS = ['django.core.files.uploadhandler.TemporaryFileUploadHandler', "django.core.files.uploadhandler.MemoryFileUploadHandler"]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'usuarios',
    'Database',
    'core',
    'utilitarios',
    'geradoc',
    'honorario_131',
    'ordem_servico',
    'recibimentos_empresarial',
    'relatorios',
    'bootstrap4',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'portal_financeiro.middlewares.GrupoAutorizadoMiddleware',
]

ROOT_URLCONF = 'portal_financeiro.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates', BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'portal_financeiro.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

#DATABASES#

system = os.path.abspath(os.sep)

# Base Produção
if system == '/':
    DATABASES = {
        'default': {
            'NAME': 'portal_financeiro',
            'ENGINE': 'django.db.backends.mysql',
            'HOST': '127.0.0.1',
            'PORT': '3306',
            'USER': 'humhub_prod',
            'PASSWORD': 'd1011p523',
        },
        'pid_db': {
            'NAME': 'pid',
            'ENGINE': 'django.db.backends.mysql',
            'HOST': '127.0.0.1',
            'PORT': '3306',
            'USER': 'humhub_prod',
            'PASSWORD': 'd1011p523',
        }
    }
else:
    # Base Desenvolvimento
    DATABASES = {
        'default': {
            'NAME': 'portal_financeiro',
            'ENGINE': 'django.db.backends.mysql',
            'HOST': '127.0.0.1',
            'PORT': '3306',
            'USER': 'root',
            'PASSWORD': 'adminroot',
        },
        'pid_db': {
            'NAME': 'pid',
            'ENGINE': 'django.db.backends.mysql',
            'HOST': '127.0.0.1',
            'PORT': '3306',
            'USER': 'root',
            'PASSWORD': 'adminroot',
        },
    }


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

MEDIA_URL = "/media/"
MEDIA_ROOT =  BASE_DIR / "media"

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

CORS_ALLOWED_ORIGINS = ['*']

CORS_ALLOW_HEADERS = (
    'X-KEY',
    'CONTENT-TYPE',
    'X-CUSTOM-TOKEN'
)

CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
CORS_ALLOW_ALL_ORIGINS = True

LOGIN_URL = 'request_login'
AUTH_USER_MODEL = 'usuarios.Usuario'
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 60 * 60  # 1 hora
CELERY_TASK_SOFT_TIME_LIMIT = 60 * 55

CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_REJECT_ON_WORKER_LOST = True