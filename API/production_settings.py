"""
Django settings for API project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '&t*j@n37kc7m$7m+q-rw=%lxcqwvde2z#qjxgo!!31ndn0o(rq'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
#DEBUG = True

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'scratch_api.apps.ScratchApiConfig',
    'course.apps.CourseConfig',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_tables2',
    'ckeditor',
    'ckeditor_uploader',
    'website',
    'production_process',
    'mobile_api',
    'ordered_model',
    'dry_rest_permissions',
    'pinax.badges',
    'django_oss_storage',	

]

INSTALLED_APPS += [
    'fluent_comments',  # must be before django_comments
    'threadedcomments',
    'crispy_forms',
    'django_comments',
    'django.contrib.sites',
]

INSTALLED_APPS += [
    'notifications',
    'qa',
    'mptt',
    'avatar',
    'taggit',
    'qr_code',
    'webshell'
]

# AUTHENTICATION_BACKENDS = (
#     'rules.permissions.ObjectPermissionBackend',
#     'django.contrib.auth.backends.ModelBackend',
# )

# AUTH_USER_MODEL = 'scratch_api.User'
AUTH_USER_MODEL = 'scratch_api.BaseUser'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'scratch_api.middleware.one_session_per_user_middleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'API.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),
                 os.path.join(BASE_DIR, 'html')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'API.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'scratchDB',
        'USER': 'root',
        'PASSWORD':'123456',
        'HOST': 'mysql',
        'PORT': '3306',
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

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

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    )
}

# 使得上传的mp3文件能够让nginx有访问权限
FILE_UPLOAD_PERMISSIONS = 0o644

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

LANGUAGES = [
    ('zh-hans', '中文简体'),
    ('en', 'English'),
]

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

MEDIA_ROOT = '/var/sb2_files/'

MEDIA_URL = '/files/'
MEDIA_URL = 'http://www.tuopinpin.com/files/'


# STATIC_ROOT = 'static/'

STATICFILES_DIRS = (
  os.path.join(BASE_DIR, 'static/'),
)

STATIC_URL = '/static/'
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

# In order to handle AJAX cross domin problem
#CORS with session and cookie set cannot user wildcard *
#CORS_ORIGIN_ALLOW_ALL = True

CORS_ORIGIN_WHITELIST = (
    'maibaoscratch.com',
    'www.maibaoscratch.com',
    'scratch.maibaoscratch.com',
    'localhost:8000',
    '127.0.0.1:8888',
    'localhost:8888',
    '127.0.0.1:9000'
)

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = (
    'GET',
    'POST',
)

CORS_ALLOW_HEADERS=(
    'Authorization',
)

# configure Broker
CELERY_BROKER_URL = 'redis://redis:6379/0'
BROKER_URL = 'redis://redis:6379/0'
CELERY_BROKER_TRANSPORT = 'redis'
# CELERY_BACKEND_URL = 'redis://127.0.0.1:6379/1'


# URL after login
LOGIN_REDIRECT_URL = '/t/index'
# URL after logout
LOGOUT_REDIRECT_URL = '/t/'

SESSION_COOKIE_HTTPONLY = False
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_DOMAIN = ".tuopinpin.com"

# TIME FORAMT
SHORT_DATETIME_FORMAT = 'Y/m/d G:i:s'

CKEDITOR_UPLOAD_PATH = "course/"
# CKEDITOR_FILENAME_GENERATOR = lambda filename: filename.upper()
CKEDITOR_IMAGE_BACKEND = 'pillow'

CKEDITOR_CONFIGS = {
    # 配置名是default时，django-ckeditor默认使用这个配置
    'default': {
        'skin': 'moono',
        # 使用简体中文
        'language': 'zh-Hans',
        'toolbar': 'full',
        # 插件
        'extraPlugins': ','.join(['codesnippet','uploadimage','widget','lineutils',]),
        'removePlugins': 'elementspath',
    },
    'qa_ckeditor': {
        # 'toolbar': 'Standard',
        'language': 'zh-Hans',
        'extraPlugins': ','.join(['codesnippet', 'uploadimage', 'widget', 'lineutils', ]),
        'removePlugins': 'elementspath',
    },
}

CRISPY_TEMPLATE_PACK = 'bootstrap3'

COMMENTS_APP = 'fluent_comments'

FLUENT_COMMENTS_USE_EMAIL_NOTIFICATION = False
FLUENT_COMMENTS_EXCLUDE_FIELDS = ('name', 'email', 'url', 'title')
FLUENT_COMMENTS_FORM_CLASS = 'API.comments.CommentForm'
PROFANITIES_LIST = {'fuck', '垃圾'}
SITE_ID = 2

# AVATAR_GRAVATAR_FIELD = 'username'
AVATAR_CACHE_ENABLED = False
AVATAR_AUTO_GENERATE_SIZES = (160, 160)
# 因为usercenter里的大小设置为160*160
#似乎开启Cache后导致更换头像有延迟，故这里设置为false
AVATAR_CLEANUP_DELETED = True
AVATAR_MAX_AVATARS_PER_USER = 1
AVATAR_DEFAULT_URL = 'img/user_img.png'
AVATAR_CHANGE_TEMPLATE = 'avatar/change_avatar.html'
AVATAR_PROVIDERS = (
    'avatar.providers.PrimaryAvatarProvider',
    'avatar.providers.DefaultAvatarProvider',
)
AVATAR_THUMB_FORMAT = 'PNG'

CSRF_COOKIE_DOMAIN = ".tuopinpin.com"
CSRF_TRUSTED_ORIGINS = ['.tuopinpin.com']



STATICFILES_STORAGE = 'django_oss_storage.backends.OssStaticStorage'

OSS_ACCESS_KEY_ID  = ""
OSS_ACCESS_KEY_SECRET  = ""
OSS_ENDPOINT = "oss-cn-hangzhou.aliyuncs.com"
#OSS_BUCKET_NAME = "scratch-upload"
OSS_STATIC_BUCKET_NAME = "scratch-upload"
OSS_MEDIA_BUCKET_NAME = "scratch-upload"
OSS_STATIC_CDN_URL = "http://static.tuopinpin.com/"
OSS_MEDIA_CDN_URL = "http://static.tuopinpin.com/"
OSS_BUCKET_ACL = "public-read"  # private, public-read, public-read-write
