from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.contrib.auth.models import User

from .methods import validateEmail, UniqueUserEmail, UniqueUserPhone
from .models import Profile
from .serializers import TokenSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_jwt.settings import api_settings
from rest_framework.permissions import AllowAny
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

# JWT settings
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


# Create your views here.
class SignupView(APIView):
	permission_classes = (AllowAny,)

	def post(self, request):
		error = False
		message = ''
		data = []
		errors = []
		res_errors = {}
		result = 'FAIL'
		response_status = HTTP_400_BAD_REQUEST

		email = request.POST.get('email')
		name = request.POST.get('name')
		password = request.POST.get('password')
		confirm_password = request.POST.get('confirm_password')
		contact_number = request.POST.get('contact_number')

		if not name:
			message = 'Please enter name.'
			errors.append(message)
			res_errors.update({'name': message})
			error = True
		if not email:
			message = 'Please enter email.'
			errors.append(message)
			res_errors.update({'email': message})
			error = True
		elif not validateEmail(email):
			message = 'Please enter valid email.'
			errors.append(message)
			res_errors.update({'email': message})
			error = True
		elif not UniqueUserEmail(email):
			message = 'Email already exist. Please enter another email.'
			errors.append(message)
			res_errors.update({'email': message})
			error = True

		if not password:
			message = 'Please enter password.'
			errors.append(message)
			res_errors.update({'password': message})
			error = True
		elif len(password) < 6:
			message = 'Password must be at least 6 digit long.'
			errors.append(message)
			res_errors.update({'password': message})
			error = True
		if not confirm_password:
			message = 'Please enter confirm password.'
			errors.append(message)
			res_errors.update({'confirm_password': message})
			error = True
		elif password and confirm_password and password != confirm_password:
			message = 'Password and confirm password did not match.'
			errors.append(message)
			res_errors.update({'confirm_password': message})
			error = True

		if not contact_number:
			message = 'Please enter contact number.'
			errors.append(message)
			res_errors.update({'contact_number': message})
			error = True
		elif len(contact_number) != 8:
			message = 'Please enter valid contact number.'
			errors.append(message)
			res_errors.update({'contact_number': message})
			error = True
		elif not UniqueUserPhone(contact_number):
			message = 'Contact number already exist. Please enter another number.'
			errors.append(message)
			res_errors.update({'contact_number': message})
			error = True

		if not error:
			try:
				# create user
				new_user = User(
					username=name.strip(),
					email=email.strip(),
					password=make_password(password),
					date_joined=timezone.now()
				)
				# save new user
				new_user.save()

				if contact_number:
					user_profile = Profile(
						contact_number=contact_number.strip(),
						user=new_user
					)
					user_profile.save()

				data = {
					'id_user': new_user.pk,
					'email': new_user.email,
					'name': new_user.username
				}
				result = 'SUCCESS'
				message = 'User successfully signed up.'
				response_status = HTTP_200_OK
			except Exception as e:
				message = str(e)
				errors.append(message)
				res_errors.update({'user_signup': message})

		return Response({
			'data': data,
			'result': result,
			'errors': errors,
			'res_errors': res_errors,
			'message': message
		},
			status=response_status
		)


class LoginView(APIView):
	permission_classes = (AllowAny,)

	def post(self, request):
		error = False
		message = ''
		data = []
		errors = []
		res_errors = {}
		result = 'FAIL'
		response_status = HTTP_400_BAD_REQUEST

		name = request.POST.get('name')
		password = request.POST.get('password')

		if not name:
			message = 'Please enter name.'
			errors.append(message)
			res_errors.update({'name': message})
			error = True
		if not password:
			message = 'Please enter password.'
			errors.append(message)
			res_errors.update({'password': message})
			error = True

		if not error:
			try:
				user = User.objects.filter(
					username__iexact=name
				).order_by('-date_joined').values('username').first()

				if user:
					user = authenticate(request, username=user.get('username'), password=password)

					if user.is_authenticated and user.is_active:
						login(request, user)

						serializer = TokenSerializer(data={
							"token": jwt_encode_handler(
								jwt_payload_handler(user)
							)
						})
						# Return a 400 response if user data is invalid
						serializer.is_valid(raise_exception=True)

						data = {
							'id_user': user.pk,
							'email': user.email,
							'name': user.username,
							'token': jwt_encode_handler(
								jwt_payload_handler(user)
							)
						}
						result = 'SUCCESS'
						message = 'User successfully logged in.'
						response_status = HTTP_200_OK

				else:
					message = 'Invalid email or password.'
					errors.append(message)
					res_errors.update({'user_login': message})

			except Exception as e:
				# raise e
				message = str(e)
				errors.append(message)
				res_errors.update({'user_login': message})

		return Response({
			'data': data,
			'result': result,
			'errors': errors,
			'res_errors': res_errors,
			'message': message
		},
			status=response_status
		)
