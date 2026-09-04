"""
Base settings for cv_adaptable_project.

Shared configuration for all environments.
"""

from pathlib import Path
import environ

env = environ.Env()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

environ.Env.read_env(BASE_DIR / ".env", overwrite=False)

# ------------------------------------------------------------------ #
# Core
# ------------------------------------------------------------------ #
SECRET_KEY = env("DJANGO_SECRET_KEY", default="django-insecure-dev-key-change-me")
ALLOWED_HOSTS: list[str] = []

# ------------------------------------------------------------------ #
# Apps
# ------------------------------------------------------------------ #
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Seguridad — bloqueo de intentos fallidos (Req. 1.3)
    "axes",
    # Apps del proyecto
    "core",
    "perfil",
    "certificados",
    "generador",
]

# ------------------------------------------------------------------ #
# Middleware
# ------------------------------------------------------------------ #
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Headers de seguridad en todas las respuestas (Req. 11.1)
    "core.middleware.SecurityHeadersMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # django-axes: debe ir después de AuthenticationMiddleware (Req. 1.3)
    "axes.middleware.AxesMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "cv_adaptable_project.urls"

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

WSGI_APPLICATION = "cv_adaptable_project.wsgi.application"

# ------------------------------------------------------------------ #
# Auth
# ------------------------------------------------------------------ #
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/login/"

# ------------------------------------------------------------------ #
# Session — Req. 1.1
# ------------------------------------------------------------------ #
SESSION_COOKIE_AGE = 28800
SESSION_COOKIE_HTTPONLY = True
SESSION_SAVE_EVERY_REQUEST = True

# ------------------------------------------------------------------ #
# django-axes — Req. 1.3
# ------------------------------------------------------------------ #
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 0.25
AXES_LOCKOUT_PARAMETERS = ["username", "ip_address"]

AUTHENTICATION_BACKENDS = [
    "axes.backends.AxesStandaloneBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# ------------------------------------------------------------------ #
# i18n
# ------------------------------------------------------------------ #
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------------ #
# Static / Media
# ------------------------------------------------------------------ #
STATIC_URL = "static/"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

CV_UPLOAD_DIR = BASE_DIR / "media" / "certificados"

# Tamaño máximo permitido para subida de certificados PDF (5 MB)
MAX_UPLOAD_SIZE = 5 * 1024 * 1024

# ------------------------------------------------------------------ #
# Misc
# ------------------------------------------------------------------ #
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
