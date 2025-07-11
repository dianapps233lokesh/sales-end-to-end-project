from django.urls import path
from .views import RegisterAPI,VerifyOTPAPI,LoginAPI
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

urlpatterns=[
    path('register/',RegisterAPI.as_view(),name='register-user'),
    path('verifyOTP/',VerifyOTPAPI.as_view(),name='verify-otp'),
    path('login/',LoginAPI.as_view(),name='login-user'),
]

urlpatterns+=[
    path('token/refresh',TokenRefreshView.as_view(),name='token-refresh'),
]