from django.urls import path
from django.contrib.auth.views import LogoutView
from rest_framework import routers

from . import views
from .views import MessageViewSet

router = routers.SimpleRouter()
router.register(r'messages', MessageViewSet, basename='Message')
urlpatterns = router.urls

app_name = 'geochats'
urlpatterns += [
    path('', views.index, name='index'),
    path('logout', LogoutView.as_view()),
    path('auth/signup/', views.signup, name='signup'),
    path('auth/login/', views.signup, name='login'),
    path('get-location/', views.ajax_get_location, name='ajax-location'),
    path('save-user/', views.ajax_save_user, name='ajax-save-user'),
    path('room/', views.room, name='room'),
    path('map-test/', views.map_test, name='map-test')
]
