from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


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
