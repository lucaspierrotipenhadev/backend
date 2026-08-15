from .base import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Acelera a execução dos testes trocando o hasher de senha
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]