from django.urls import path
from .views import RegisterAPI,VerifyOTPAPI,LoginAPI,check,LogoutAPI,UpdateProfileAPIView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns=[
    path('register/',RegisterAPI.as_view(),name='register-user'),
    path('verifyOTP/',VerifyOTPAPI.as_view(),name='verify-otp'),
    path('login/',LoginAPI.as_view(),name='login-user'),
    path('check/',check.as_view(),name='check'),
    path('logout/',LogoutAPI.as_view(),name='logout'),
    path('update/',UpdateProfileAPIView.as_view(),name='update')
]

urlpatterns+=[
    path('token/refresh/',TokenRefreshView.as_view(),name='token-refresh'),
]