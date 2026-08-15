"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import sys
import os

from django.core.wsgi import get_wsgi_application
from pathlib import Path

# Adiciona o diretório 'apps' e 'backend' no sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR / 'apps'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')