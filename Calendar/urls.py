from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('validate/',views.ValidateUser.as_view(),name='validate-user'),
    path('get-calendars/',views.GetCalendars.as_view(),name='Get-calendars'),
    path('get-events/<str:calendar_id>/',views.GetEvents.as_view(),name='Get-events')
]
