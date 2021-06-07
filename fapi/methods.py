from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
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
