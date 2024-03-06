from django.urls import path

from . import views

urlpatterns = [
    path('', views.mainpage, name='mainpage'),
    path('upload', views.upload_file, name='upload'),
    #path('download',views.list_files,name='download'),
    path('download/<str:filename>', views.download_file, name='download_file'),
    path('download/', views.list_files, name='list_files'),
    path('logout/',views.logout,name="logout"),
    path('login/',views.login,name="login"),

]