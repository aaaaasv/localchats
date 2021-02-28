from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('get-location/', views.ajax_get_location, name='ajax-location'),
    path('<str:room_name>/', views.room, name='room'),
]