from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Banco de dados para desenvolvimento local (SQLite por simplicidade ou Postgres local)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Permitir CORS local para SPA (React, Vue, Next.js, etc.)
CORS_ALLOW_ALL_ORIGINS = True