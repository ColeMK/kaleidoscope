from django.urls import path

from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('upload', views.upload_file, name='upload'),
    path('download/<str:filename>', views.download_file, name='download_file'),
    path('download/', views.list_files, name='list_files'),
    path('logout/',views.logout,name="logout"),
    path('mainpage/',views.mainpage,name="mainpage"),
    path('signin_wait/',views.signin_wait,name="signin_wait"),
    path('create_account/',views.create_acc_page,name="create_account"),
    path('create_account_work/',views.create_acc_work,name="creating_account"),
]