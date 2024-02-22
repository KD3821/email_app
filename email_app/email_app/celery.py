import os
from celery import Celery


os.environ.setdefault("DJANGO_SETTING_MODULE", "email_app.settings")
app = Celery("email_app")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
