from pathlib import Path
import os
from dotenv import load_dotenv
from datetime import timedelta
import psycopg2


# load .env file to access variables
load_dotenv()
django_secret_key = os.getenv('DJANGO_SECRET_KEY')

# PostgreSQL database variables
postgresql_name = os.getenv('PGDATABASE')
postgresql_user = os.getenv('PGUSER')
postgresql_password = os.getenv('PGPASSWORD')
postgresql_host = os.getenv('PGHOST')
postgresql_port = os.getenv('PGPORT')

# import email and password
my_email = os.getenv('MY_EMAIL')
my_email_password = os.getenv('MY_EMAIL_PASSWORD')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = django_secret_key

DEBUG = False

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
]

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'z12-backend-production.up.railway.app'
]

MEDIA_ROOT = '../media'

# Application definition

CORS_ORIGIN_WHITELIST = [
    'http://localhost:3000',
    'https://z12-frontend-production.up.railway.app'
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',
    'login_register_app',
    'get_dropdown_data_app',
    'user_details_app',
    'payment_processing_app',
    'metric_gathering_app',
    'populate_dashboard_app',
    'chart_data_app',
    'update_info_app',
]


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'TOKEN_EXPIRE_TIME': timedelta(hours=1)
}

AUTH_USER_MODEL = 'login_register_app.User'

ROOT_URLCONF = 'z12_server.urls'

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

WSGI_APPLICATION = 'z12_server.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': postgresql_name,
        'HOST': postgresql_host,
        'PORT': postgresql_port,
        'USER': postgresql_user,
        'PASSWORD': postgresql_password,
    }
}

# email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = my_email
EMAIL_HOST_PASSWORD = my_email_password

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
