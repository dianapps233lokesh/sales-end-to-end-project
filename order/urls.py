from django.urls import path,include
from .views import OrderAPI

urlpatterns = [
    path('order/',OrderAPI.as_view(),name="order-crud")
]
