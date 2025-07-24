from django.urls import path
from .views import RegisterAPI,VerifyOTPAPI,LoginAPI,LogoutAPI,UpdateProfileAPIView,Userlist,ActivateDeactivateView,generate_users_csv
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns=[
    path('register/',RegisterAPI.as_view(),name='register-user'),
    path('verifyOTP/',VerifyOTPAPI.as_view(),name='verify-otp'),
    path('login/',LoginAPI.as_view(),name='login-user'),
    path('logout/',LogoutAPI.as_view(),name='logout'),
    path('update/',UpdateProfileAPIView.as_view(),name='update')
]

urlpatterns+=[
    path('token/refresh/',TokenRefreshView.as_view(),name='token-refresh'),
]

urlpatterns+=[
    path('userlist/',Userlist.as_view(),name='user-list'),
    path('Activate_Deactivate/<int:user_id>/',ActivateDeactivateView.as_view(),name='active-deactive-userapi'),
    path('generate-csv/',generate_users_csv,name='generate_csv'),
]