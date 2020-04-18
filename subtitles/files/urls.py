from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload_file/', views.upload_file),
    path('check_files/', views.check_files),
    path('delete_file/', views.delete_file),
    path('send_message/', views.send_message),
    path('delete_message/', views.delete_message),
    path('get_messages/', views.get_messages),
    path('get_current_user/', views.get_current_user),
]