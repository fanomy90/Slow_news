import os
from pathlib import Path
from celery.schedules import crontab
# from dotenv import load_dotenv

# load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
APPS_DIR = ROOT_DIR / "puppeteer"

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-bg8yodc#l^002n4!oy-gpikrp!c&78pxm#86anqh8wr_f$o#31'

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = True
# DEBUG = False
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    'daphne',
	'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
	'news',
    'channels',
    # 'django_celery_beat',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://95.29.204.228:80",
    "https://95.29.204.228:443",
    "https://slow-news.sytes.net"
    # "https://slow-news.sytes.net:443"
    # "https://slow-news.sytes.net:80"
    ]

CSRF_TRUSTED_ORIGINS = [
    'https://slow-news.sytes.net',
]

ROOT_URLCONF = 'puppeteer.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'puppeteer.wsgi.application'
ASGI_APPLICATION = "puppeteer.asgi.application"
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis", 6379)],
        },
    },
}
#sqlite3
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
#postgre
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': 'postgres', # Здесь используется имя службы PostgreSQL контейнера
        'PORT': 5432,
        'NAME': 'slow_news',
        'USER': 'puppeteer',
        'PASSWORD': 'puppeteer',
    }
}

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

LANGUAGE_CODE = 'ru'

# TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True
TIME_ZONE = 'Europe/Moscow'

STATIC_URL = '/static/'
# STATIC_ROOT = os.path.join(BASE_DIR, STATIC_URL)
STATIC_ROOT = os.path.join(BASE_DIR, '/yt/static/')
# STATIC_URL = '/static/'
# STATIC_ROOT = '/yt/staticfiles'
# STATICFILES_DIRS = [
#     '/yt/static',
# ]
STATICFILES_DIRS = []

# STATIC_URL = '/static/'
# STATIC_ROOT = str(ROOT_DIR / 'static')
# STATICFILES_DIRS = [
#     '/yt/static',  # Updated path
# ]
# STATICFILES_DIRS = [BASE_DIR / 'puppeteer' / 'static']  # Папка, где Django ищет файлы

# STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# STATIC_URL = '/static/'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# MEDIA_URL = '/media/'
# STATICFILES_DIRS = []

# STATIC_ROOT = str(ROOT_DIR / "staticfiles")
# STATIC_URL = "/static/"
# STATICFILES_DIRS = [
#     str(APPS_DIR / "static"),
# ]

# STATICFILES_FINDERS = [
#     "django.contrib.staticfiles.finders.FileSystemFinder",
#     "django.contrib.staticfiles.finders.AppDirectoriesFinder",
# ]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



# настройки celery
CELERY_BROKER_URL = 'redis://redis:6379'
CORS_ALLOW_ALL_ORIGINS = True
CELERY_RESULT_BACKEND = 'redis://redis:6379'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

# Новая опция для предотвращения предупреждения в Celery 6.0 и выше
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
# периодическая задача
# CELERY_BEAT_SHEDULE = {
#     'download_a_news_beat' : {
#         'task': 'news.tasks.download_a_news_beat',
#         'shedule': 50
#     },
# }

CELERY_BEAT_SCHEDULE = {
    'import-daily-news-every-hour': {
        'task': 'news.tasks.download_a_news_beat',
        # 'schedule': crontab(hour=9, minute=0),  # Каждое утро в 9:00
        'schedule': crontab(minute=0, hour='*/3'),  # Каждый час
        #'schedule': crontab(minute='*/5'),  #Каждые 15 минут
    },
    'send-daily-news-every-hour': {
        'task': 'news.tasks.send_daily_news',
        # 'schedule': crontab(hour=9, minute=0),  # Каждое утро в 9:00
        'schedule': crontab(minute=5, hour='*/1'),  # Каждый час
        #'schedule': crontab(minute='*/2'),  # Каждые 2 минут
    },

    'send-news-every-hour': {
        'task': 'news.tasks.send_news_every_hour',
        # 'schedule': crontab(hour=9, minute=0),  # Каждое утро в 9:00
        'schedule': crontab(minute=10, hour='*/1'),  # Каждый час
        #'schedule': crontab(minute='*/2'),  # Каждые 2 минут
    },
    # 'send_news_every_3hour': {
    #     'task': 'news.tasks.send_news_every_3hour',
    #     'schedule': crontab(minute=5, hour='*/3'),  # Каждые 3 часа
    # },
    # 'send_news_every_6hour': {
    #     'task': 'news.tasks.send_news_every_6hour',
    #     'schedule': crontab(minute=5, hour='*/6'),  # Каждые 6 часа
    # },
    # 'send_news_every_9hour': {
    #     'task': 'news.tasks.send_news_every_9hour',
    #     'schedule': crontab(minute=5, hour='*/9'),  # Каждые 9 часов
    # },
    # 'send_news_every_12hour': {
    #     'task': 'news.tasks.send_news_every_12hour',
    #     'schedule': crontab(minute=5, hour='*/12'),  # Каждые 12 часов
    # },
    # 'send_news_daily': {
    #     'task': 'news.tasks.send_news_daily',
    #     'schedule': crontab(minute=5, hour='*/24'),  # Каждые 24 часов
    # },
}