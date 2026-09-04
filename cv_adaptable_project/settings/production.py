"""
Production settings for cv_adaptable_project.
"""

import environ
from .base import *  # noqa: F401,F403

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env", overwrite=False)  # noqa: F405

DEBUG = False

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=[])

# ------------------------------------------------------------------ #
# Database — MySQL
# ------------------------------------------------------------------ #
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST", default="127.0.0.1"),
        "PORT": env("DB_PORT", default="3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# ------------------------------------------------------------------ #
# WhiteNoise — static files
# ------------------------------------------------------------------ #
# WhiteNoiseMiddleware debe ir lo más arriba posible, justo después de
# SecurityMiddleware. Insertamos el resto del stack base después de él.
if "whitenoise.middleware.WhiteNoiseMiddleware" not in MIDDLEWARE:  # noqa: F405
    base_middleware = list(MIDDLEWARE)  # noqa: F405
    base_middleware.remove("core.middleware.SecurityHeadersMiddleware")
    MIDDLEWARE = [  # noqa: F811
        "django.middleware.security.SecurityMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware",
        "core.middleware.SecurityHeadersMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "axes.middleware.AxesMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]

STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ------------------------------------------------------------------ #
# Security
# ------------------------------------------------------------------ #
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"
