from django.urls import path,include
# from .views import OrderAPI

# urlpatterns = [
#     path('order/',OrderAPI.as_view(),name="order-crud"),
#     path('order/<int:pk>/',OrderAPI.as_view(),name="order-update"),
# ]


from .views import OrderViewSet
from rest_framework.routers import DefaultRouter

router=DefaultRouter()

router.register(f'orders',OrderViewSet,basename='order')
# print(router.urls)

urlpatterns=router.urls
