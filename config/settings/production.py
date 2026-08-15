import dj_database_url
from .base import *

DEBUG = False

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*.railway.app").split(",")

db_url = os.getenv("DATABASE_PUBLIC_URL") or os.getenv("DATABASE_URL")

DATABASES = {
    "default": dj_database_url.config(
        default=db_url,
        conn_max_age=60,
        conn_health_checks=True,
        #ssl_require=True,
    )
}

CSRF_TRUSTED_ORIGINS = os.getenv(
    "CSRF_TRUSTED_ORIGINS", 
    "https://*.railway.app"
).split(",")

CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

# Origens autorizadas no CORS para produção
CORS_ALLOWED_ORIGINS = [
    # "https://seu-frontend.com",
]