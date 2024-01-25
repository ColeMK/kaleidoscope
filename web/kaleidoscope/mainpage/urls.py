from django.urls import path

from . import views

urlpatterns = [
    path('', views.mainpage, name='mainpage'),
    path('upload', views.upload_file, name='upload'),
    path('download',views.download_file,name='download')
]