from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import Parent
User=get_user_model()

# Create your models here.


class AuthInfo(Parent):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    access_token=models.TextField()
    refresh_token=models.TextField()
    expiry=models.DateTimeField()
    token_uri=models.TextField(default="https://oauth2.googleapis.com/token")
    client_id=models.TextField()
    client_secret=models.TextField()
    scopes=models.TextField()