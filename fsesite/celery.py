import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fsesite.settings')

app = Celery('fsesite')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
	'files-update-ses-score': {
		'task': 'calculate_ses_score',
		'schedule': 300.0,
	}
}
