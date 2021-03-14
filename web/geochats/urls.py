from django.urls import path

from . import views

app_name = 'geochats'
urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('get-location/', views.ajax_get_location, name='ajax-location'),
    path('save-user/', views.ajax_save_user, name='ajax-save-user'),
    path('room/', views.room, name='room'),
    path('map-test/', views.map_test, name='map-test')
]