from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)


class Upload(models.Model):
    id_file_upload = models.AutoField(primary_key=True)
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_path = models.FilePathField()
    file_size = models.BigIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ses_score = models.IntegerField(default=0)
    created_date = models.DateTimeField(default=timezone.now)
    modified_date = models.DateTimeField(auto_now=True)
