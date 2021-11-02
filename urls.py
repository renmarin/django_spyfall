from django.urls import path

from . import views

app_name = 'spyfall'
urlpatterns = [
    path('', views.index, name='index'),
    path('room/<str:room_id>/', views.room, name='room'),
    path('control_room/<str:room_id>/', views.control_room, name='control_room'),
]
