from django.urls import path
from knox import views as knox_views

from auth import api


app_name = 'auth'

urlpatterns = [
    path('login/', api.LoginAPI.as_view(), name='login'),
    path('logout/', knox_views.LogoutView.as_view(), name='logout'),
    path('register/', api.RegisterAPI.as_view(), name='register'),
    path('checkifexists/<str:username>/', api.CheckIfUsernameIsFree.as_view(),
         name='check_if_username_is_free'),
]