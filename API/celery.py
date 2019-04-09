# coding:utf-8
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery, platforms

# set the default Django settings module for the 'celery' program.
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'API.production_settings')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'API.settings')

app = Celery('API')

# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

platforms.C_FORCE_ROOT = True #加上这一行
# app.conf.update(
#     task_serializer='pickle',）
app.conf.update(
    task_serializer='pickle',
    accept_content=['json', 'pickle']
)
# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
