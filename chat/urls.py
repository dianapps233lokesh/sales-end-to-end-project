from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('<str:other_username>/',views.lobby,name='chat')
]
