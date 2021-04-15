from __future__ import absolute_import, unicode_literals
import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbk_gos.settings')

app = Celery('fbk_gos')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


app.conf.beat_schedule = {
    'get-contracts-with-parser-status-0': {
        'task': 'zakupki.tasks.get_contract_short',
        'schedule': 1.0,
    },
    'get-contracts-with-parser-status-1': {
        'task': 'zakupki.tasks.get_contract_full',
        'schedule': 3.0,
    },
}