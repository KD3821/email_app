import os

from celery import Celery


os.environ.setdefault("DJANGO_SETTING_MODULE", "email_app.settings")
app = Celery("email_app")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


"""
export DJANGO_SETTINGS_MODULE=email_app.settings
python3 -m celery -A email_app worker --loglevel=info
python3 -m celery -A email_app beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
"""