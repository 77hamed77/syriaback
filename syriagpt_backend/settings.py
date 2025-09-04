# syriagpt_backend/settings.py

import os
from pathlib import Path
from decouple import config
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# CORE SETTINGS
# ==============================================================================

# اقرأ المفتاح السري من متغيرات البيئة
SECRET_KEY = config('SECRET_KEY')

# اقرأ حالة DEBUG من متغيرات البيئة (الافتراضي هو False للإنتاج)
DEBUG = config('DEBUG', default=False, cast=bool)

# اقرأ المضيفين المسموح بهم من متغيرات البيئة
# سيقرأ "syriagpt_backend.onrender.com,localhost" ويقسمها إلى قائمة
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='127.0.0.1,localhost').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # المكتبات الخارجية
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'storages', # <-- مكتبة لتخزين الملفات على S3

    # تطبيقاتنا
    'users',
    'chat',
    'qa',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise لخدمة الملفات الثابتة بكفاءة
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'syriagpt_backend.urls'
WSGI_APPLICATION = 'syriagpt_backend.wsgi.application'
AUTH_USER_MODEL = 'users.CustomUser'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ==============================================================================
# DATABASE
# ==============================================================================
# استخدم dj-database-url لقراءة DATABASE_URL من متغيرات البيئة
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL'),
        conn_max_age=600
    )
}

# ==============================================================================
# PASSWORD VALIDATION
# ==============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==============================================================================
# INTERNATIONALIZATION
# ==============================================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ==============================================================================
# STATIC & MEDIA FILES (مهم جدًا للإنتاج)
# ==============================================================================
# إعدادات الملفات الثابتة (CSS, JS)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# إعدادات ملفات الوسائط (الصور المرفوعة من المستخدمين) باستخدام Supabase S3
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = config('SUPABASE_S3_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('SUPABASE_S3_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('SUPABASE_S3_BUCKET_NAME')
AWS_S3_ENDPOINT_URL = config('SUPABASE_S3_ENDPOINT_URL')
AWS_S3_REGION_NAME = config('SUPABASE_S3_REGION_NAME')
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}
AWS_LOCATION = 'media' # سيتم إنشاء مجلد 'media' داخل الـ bucket
MEDIA_URL = f'{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/{AWS_LOCATION}/'

# ==============================================================================
# API & CORS SETTINGS
# ==============================================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework_simplejwt.authentication.JWTAuthentication',),
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated',]
}

from datetime import timedelta
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

# اقرأ روابط الواجهة الأمامية المسموح بها من متغيرات البيئة
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:3000').split(',')

# ==============================================================================
# DEFAULT PRIMARY KEY
# ==============================================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'