import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable not set")

DEBUG = os.getenv("DEBUG", "0").lower() in ("1", "true", "yes", "y", "t")

if DEBUG:
    ALLOWED_HOSTS = ["*"]
else:
    ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")


DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "drf_spectacular",
    "rest_framework_simplejwt",
    "channels"
]

LOCAL_APPS = [
    "apps.accounts",
    "apps.chat",
    "apps.community",
    "apps.core",
    "apps.daily",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": os.getenv("POSTGRES_PORT"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "ko-kr"

TIME_ZONE = "Asia/Seoul"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",  # 임시 복구
        "apps.accounts.authentication.CookieOrHeaderJWTAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "EXCEPTION_HANDLER": "apps.core.exceptions.custom_exception_handler",
}

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

if not REDIS_HOST or not REDIS_PORT:
    raise ValueError("REDIS_HOST and REDIS_PORT must be set")
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

POST_VIEW_TTL_SECONDS = 60 * 10

AUTH_USER_MODEL = "accounts.User"

# SimpleJWT 기본값
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(hours=24),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# 로드밸런서에서 Https로 들어온 요청을 Http로 받는데, 다시 Https로 조정
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# access 쿠키 옵션
AUTH_ACCESS_COOKIE_NAME = "access"
AUTH_ACCESS_COOKIE_PATH = "/"
AUTH_ACCESS_COOKIE_SECURE = not DEBUG
AUTH_ACCESS_COOKIE_HTTPONLY = True
AUTH_ACCESS_COOKIE_SAMESITE = "Lax"

# refresh 쿠키 옵션
AUTH_REFRESH_COOKIE_NAME = "refresh"
AUTH_REFRESH_COOKIE_PATH = "/"
AUTH_REFRESH_COOKIE_SECURE = not DEBUG
AUTH_REFRESH_COOKIE_HTTPONLY = True
AUTH_REFRESH_COOKIE_SAMESITE = "Lax"

# 로그인 연속 실패 기준
LOGIN_FAIL_BLOCK_COUNT_1 = 5
LOGIN_FAIL_BLOCK_COUNT_2 = 10

# 로그인 연속 실패시 차단 시간
LOGIN_FAIL_BLOCK_TIME_1 = 60 * 10  # 10분
LOGIN_FAIL_BLOCK_TIME_2 = 60 * 60  # 1시간

# 로그인 연속 실패 기준 시간
LOGIN_FAIL_COUNTER_TTL = 60 * 60 * 2  # 2시간

# Access Token
JWT_ACCESS_TOKEN_LIFETIME = 60 * 60  # 1시간

# Refresh Token
JWT_REFRESH_TOKEN_LIFETIME = 60 * 60 * 24  # 24시간
JWT_REFRESH_TOKEN_LIFETIME_REMEMBERME = 60 * 60 * 24 * 30  # 30일

# 이메일/닉네임 중복 확인 만료 시간
SIGNUP_CHECK_TTL = 60 * 5  # 5분

# 이메일 인증
EMAIL_VERIFICATION_TTL = 60 * 3
EMAIL_VERIFICATION_COOLDOWN = 30
EMAIL_VERIFICATION_MAX_ATTEMPTS = 5
EMAIL_VERIFICATION_LIMIT_PER_HOUR = 3

# Gmail SMTP
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER or "")

# JWT 검증 토큰
VERIFY_TOKEN_ALGO = "HS256"
VERIFY_TOKEN_EXPIRES_SECONDS = 10 * 60

# 비밀번호 유효성 정책
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

#실시간 채팅 웹소켓
ASGI_APPLICATION = "config.routing.application"

CHANNEL_LAYER = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [("redis", 6379)]},
    }
}
# OAuth (Google/Kakao)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "")

KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID", "")
KAKAO_CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET", "")
KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI", "")
