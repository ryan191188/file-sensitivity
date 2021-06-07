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

    def __init__(self, *args, **kwargs):
        super(Upload, self).__init__(*args, **kwargs)
        self.__ses_score = self.ses_score

    def save(self, *args, **kwargs):
        if self.ses_score > self.__ses_score:
            self.modified_date = timezone.now()
        super(Upload, self).save(*args, **kwargs)


class WordSensitivity(models.Model):
    id_word_ses = models.AutoField(primary_key=True)
    sensitive_word = models.CharField(max_length=255, blank=True, null=True)
    score = models.IntegerField(default=0)
    created_date = models.DateTimeField(default=timezone.now)
