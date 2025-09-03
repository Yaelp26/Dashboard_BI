"""
WSGI config for dataset_dashboard project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dataset_dashboard.settings')

from whitenoise import WhiteNoise
application = WhiteNoise(application)

application = get_wsgi_application()
