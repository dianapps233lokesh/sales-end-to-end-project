from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import random
from django.contrib.auth.password_validation import validate_password


class MyUser(AbstractUser):
    username=models.CharField(max_length=100, unique=True)
    email=models.EmailField(unique=True)
    password=models.CharField(max_length=100,validators=[validate_password])
    confirm_password=models.CharField(max_length=100)


class OTP(models.Model):
    user=models.ForeignKey(MyUser,on_delete=models.CASCADE)
    otp_code=models.CharField(max_length=6)
    created_at=models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return self.created_at >= timezone.now()-timezone.timedelta(minutes=10)

    def generate_otp(self):
        return random.randint(100000,999999)

