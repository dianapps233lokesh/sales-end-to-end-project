from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import random
from django.contrib.auth.password_validation import validate_password
from django.conf import settings 


class Parent(models.Model):
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        abstract=True

class MyUser(Parent,AbstractUser):
    email=models.EmailField(unique=True)


    def __str__(self):
        return self.email
  

class OTP(Parent):
    mail = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    data = models.JSONField()


    def is_valid(self):
        return self.updated_at >= timezone.now()-timezone.timedelta(minutes=10)

 
    