from celery import shared_task
from celery.utils.log import get_task_logger
from fapi.models import Upload
from fapi.methods import calculate_ses
from django.utils import timezone

logger = get_task_logger(__name__)


@shared_task(name='calculate_ses_score')
def calculate_ses_score():
	logger.info("Calculating SES Score of Files")

	files = Upload.objects.all().values('id_file_upload', 'file_name')
	for f in files:
		ses_score = calculate_ses(f['file_name'])
		if ses_score > 0:
			Upload.objects.filter(pk=f['id_file_upload']).update(
				ses_score=ses_score,
				modified_date=timezone.now()
			)
