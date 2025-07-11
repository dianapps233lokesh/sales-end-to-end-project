from django.contrib import admin

# Register your models here.
# admin.site.register
from  .models import MyUser

admin.site.register(MyUser)