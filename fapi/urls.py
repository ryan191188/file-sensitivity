from django.urls import path, include
from .views import *

urlpatterns = [
	# path('', views.index, name='index'),
	path('signup/', SignupView.as_view(), name='signup'),
	path('login/', LoginView.as_view(), name='login'),
	path('file-upload/', FileUpload.as_view(), name='file-upload'),
	path('file-listing/', MyFile.as_view(), name='file-listing'),
]
