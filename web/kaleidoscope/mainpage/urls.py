from django.urls import path

from . import views

urlpatterns = [
    #path('', views.mainpage, name='mainpage'),
    path('', views.upload_file, name='upload')
]