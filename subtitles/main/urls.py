from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/profile/', views.profile),
    path('upload_file/', views.upload_file),
    path('check/<str:word>', views.check_word),
    path('touch/<str:word>', views.touch_word),
    path('check_vocabulary/<str:word>', views.check_vocabulary_word),
    path('get_text/', views.get_text),
    path('translate/<str:word>', views.translate),
]
