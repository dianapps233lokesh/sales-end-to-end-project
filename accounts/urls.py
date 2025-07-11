from django.urls import path
from .views import RegisterAPI,VerifyOTPAPI


urlpatterns=[
    path('register/',RegisterAPI.as_view(),name='register-user'),
    path('verifyOTP/',VerifyOTPAPI.as_view(),name='verify-otp')
]