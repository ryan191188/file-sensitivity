from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import datetime
from django.contrib.auth.models import User
from django.db.models import Q

from .methods import validateEmail, UniqueUserEmail, UniqueUserPhone, validate_text_file, upload_file
from .models import Profile, Upload
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


class FileUpload(APIView):
	def post(self, request):
		error = False
		message = ''
		data = []
		errors = []
		res_errors = {}
		result = 'FAIL'
		response_status = HTTP_400_BAD_REQUEST

		text_file = request.FILES.get('text_file')

		if text_file is None:
			message = 'Please upload file.'
			errors.append(message)
			res_errors.update({'file': message})
			error = True
		elif not validate_text_file(text_file):
			message = 'Incorrect file extension not matching .txt'
			errors.append(message)
			res_errors.update({'file_ext': message})
			error = True

		if not error:
			try:
				if text_file is not None:
					err_status, upload_url = upload_file(text_file)
					if err_status:
						message = 'Error in uploading file.'
						errors.append(message)
						res_errors.update({'file_upload': message})
					else:
						file_upload = Upload(
							file_name=text_file.name,
							file_path=upload_url,
							file_size=text_file.size,
							user=request.user
						)
						file_upload.save()

						result = 'SUCCESS'
						message = 'File successfully uploaded'
						response_status = HTTP_200_OK

			except Exception as e:
				# raise e
				message = str(e)
				errors.append(message)
				res_errors.update({'file_upload': message})

		return Response({
			'data': data,
			'result': result,
			'errors': errors,
			'res_errors': res_errors,
			'message': message
		},
			status=response_status
		)


class MyFile(APIView):
	def post(self, request):
		error = False
		message = ''
		data = []
		errors = []
		res_errors = {}
		result = 'FAIL'
		response_status = HTTP_400_BAD_REQUEST

		upload_date = request.POST.get('upload_date')
		from_date = request.POST.get('from_date')
		to_date = request.POST.get('to_date')
		file_name = request.POST.get('file_name')
		size_category = request.POST.get('size_category')  # file_size
		ses_sort = request.POST.get('ses_sort')  # ses score
		page = request.POST.get('page')

		if page is None:
			message = 'Page is missing'
			errors.append(message)
			res_errors.update({'file_pagination': message})
			error = True

		if file_name and '.txt' not in file_name:
			message = 'Pls add txt extension'
			errors.append(message)
			res_errors.update({'file_name': message})
			error = True

		if size_category and size_category.lower() not in ('small', 'medium', 'large'):
			message = 'Invalid File Size Category'
			errors.append(message)
			res_errors.update({'file_size': message})
			error = True

		if from_date and not to_date:
			message = 'End Date is missing'
			errors.append(message)
			res_errors.update({'file_filter': message})
			error = True

		if to_date and not from_date:
			message = 'Start Date is missing'
			errors.append(message)
			res_errors.update({'file_filter': message})
			error = True

		if not error:
			try:
				page = int(request.POST['page'])

				if page > 1:
					# 10 files per page
					page = (page - 1) * 10
				else:
					page = 0

				qs = Upload.objects.filter(
					user=request.user
				)

				if file_name:
					qs = qs.filter(
						Q(file_name__icontains=file_name) |
						Q(file_path__icontains=file_name)
					)

				small_size = 5 * 1024
				medium_size = 5 * 1024 * 1024

				if size_category == 'small':
					qs = qs.filter(file_size__lt=small_size)
				elif size_category == 'medium':
					qs = qs.filter(file_size__range=(small_size, medium_size))
				elif size_category == 'large':
					qs = qs.filter(file_size__gt=medium_size)

				if upload_date:
					upload_start_date = datetime.strptime(
						upload_date + " 00:00:00", "%Y-%m-%d %H:%M:%S"
					)
					upload_end_date = datetime.strptime(
						upload_date + " 23:59:59", "%Y-%m-%d %H:%M:%S"
					)

					qs = qs.filter(created_date__range=[upload_start_date, upload_end_date])

				if from_date and to_date:
					upload_start_date = datetime.strptime(
						from_date + " 00:00:00", "%Y-%m-%d %H:%M:%S"
					)
					upload_end_date = datetime.strptime(
						to_date + " 23:59:59", "%Y-%m-%d %H:%M:%S"
					)

					qs = qs.filter(created_date__range=[upload_start_date, upload_end_date])

				if ses_sort == '1':
					qs = qs.order_by('-ses_score')
				else:
					qs = qs.order_by('-modified_date')

				data = qs.values(
					'id_file_upload',
					'modified_date',
					'file_name',
					'file_size',
					'ses_score'
				)[page:(page + 10)]

				if len(data) > 0:
					for o in data:
						o['last_modified'] = str(
							timezone.localtime(o['modified_date']).strftime("%d-%m-%Y")) + ' ' \
							+ str(timezone.localtime(o['modified_date']).strftime("%I:%M %p"))

						o['file_size'] = str(o['file_size']) + ' B'

					message = 'Files successfully listed.'
					result = 'SUCCESS'
					response_status = HTTP_200_OK
				else:
					message = 'No files found.'
					result = 'SUCCESS'
					response_status = HTTP_200_OK

			except Exception as e:
				message = str(e)
				errors.append(message)
				res_errors.update({'file_listing': message})

		return Response({
			'data': data,
			'result': result,
			'errors': errors,
			'message': message
		},
			status=response_status
		)
