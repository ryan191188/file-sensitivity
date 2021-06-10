from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from .models import WordSensitivity
from django.conf import settings
from os.path import splitext
import os


def validateEmail(email):
	try:
		validate_email(email)
		return True
	except ValidationError:
		return False


def UniqueUserEmail(email):
	try:
		user = User.objects.filter(
			email__iexact=email
		)

		users_count = user.count()

		if users_count > 0:
			return False
		else:
			return True
	except User.DoesNotExist:
		return True


def UniqueUserPhone(contact_number):
	try:
		user = User.objects.filter(
			profile__contact_number__iexact=contact_number
		)

		users_count = user.count()

		if users_count > 0:
			return False
		else:
			return True
	except User.DoesNotExist:
		return True


def validate_text_file(file):
	ext = splitext(file.name)[1][1:].lower()

	if ext == 'txt':
		return True
	else:
		return False


def upload_file(file, delete_later=True):
	error = False
	file_url = ''

	try:
		fs = FileSystemStorage()
		filename = fs.save(file.name, file)
		uploaded_file_url = fs.url(filename)
		# /media/<file name>

		if not delete_later:
			if os.path.isfile('media/' + filename):
				os.remove('media/' + filename)

		file_url = uploaded_file_url
	except FileNotFoundError:
		print('file not found')
		error = True

	return error, file_url


def calculate_ses(file):
	ses_score = 0

	if not isinstance(file, str):
		raise ValueError('Invalid Type')
	elif '.txt' not in file or 'media' in file:
		raise ValueError('Invalid File Name')

	try:
		targets = WordSensitivity.objects.all().values('sensitive_word', 'score')

		target_dict = {word['sensitive_word']: word['score'] for word in targets}

		word_score = {word['sensitive_word']: 0 for word in targets}

		with open(os.path.join(settings.MEDIA_ROOT, file), 'r') as source:
			for cnt, line in enumerate(source):
				line = line.strip().lower()
				# print("Line {}: {}".format(cnt, line))
				if line:
					word_list = line.split()
					for word in word_list:
						# each word in line
						if word in target_dict:
							word_score[word] += target_dict[word]

		print('WORD SCORE====')
		print(word_score)

		ses_score = sum(word_score.values())

	except FileNotFoundError:
		print('file not found')
	except ValueError:
		print('Invalid File')

	return ses_score
