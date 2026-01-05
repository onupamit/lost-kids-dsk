import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alert_system.settings')

app = Celery('alert_system')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()