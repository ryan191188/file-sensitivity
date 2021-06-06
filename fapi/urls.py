from django.urls import path, include
from .views import *

urlpatterns = [
	# path('', views.index, name='index'),
	path('signup/', SignupView.as_view(), name='signup'),
]
