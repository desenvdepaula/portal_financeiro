import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal_financeiro.settings')

app = Celery('portal_financeiro')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()