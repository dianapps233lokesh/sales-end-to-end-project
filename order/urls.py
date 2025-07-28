from django.urls import path,include
from .views import OrderAPI
from django.urls import re_path

urlpatterns = [
re_path(r'^(?P<version>v1|v2)/orders/$', OrderAPI.as_view(), name='order-list'),
    path('order/<int:pk>/',OrderAPI.as_view(),name="order-update"),
]


# from .views import OrderViewSet
# from rest_framework.routers import DefaultRouter

# router=DefaultRouter()

# router.register(f'orders',OrderViewSet,basename='order')
# # print(router.urls)

# urlpatterns=router.urls
