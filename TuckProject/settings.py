from pathlib import Path
import environ
import os

# ============================ CHECKPOINT ============================
# BackUp - 1 Homepage / Breadcrumbs / Product listing / Product Category
# ============================ CHECKPOINT ============================

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environment variables
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))  # .env should be in project root (same as manage.py)

# ============================ SECURITY ============================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['127.0.0.1', 'localhost'])

# ============================ APPLICATIONS ============================

INSTALLED_APPS = [
    # Django default apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'dynamic_breadcrumbs',

    # Local apps
    'userFolder.userprofile',
    'userFolder.products',
    'userFolder.accounts',
]

# ============================ MIDDLEWARE ============================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ============================ URLS / WSGI ============================

ROOT_URLCONF = 'TuckProject.urls'
WSGI_APPLICATION = 'TuckProject.wsgi.application'

# ============================ TEMPLATES ============================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'dynamic_breadcrumbs.context_processors.breadcrumbs',
            ],
        },
    },
]

# ============================ DATABASE ============================

DATABASES = {
    'default': env.db(),  # Reads DATABASE_URL from .env
}

# Example .env line:
# DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/DBNAME

# ============================ PASSWORD VALIDATION ============================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================ INTERNATIONALIZATION ============================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ============================ STATIC & MEDIA ============================

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# For production (collectstatic)
STATIC_ROOT = BASE_DIR / 'staticfiles'


# ============================ DEFAULT PRIMARY KEY ============================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
