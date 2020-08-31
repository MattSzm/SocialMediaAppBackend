from django.urls import path
from auth import api
from knox import views as knox_views


app_name = 'auth'

urlpatterns = [
    path('login/', api.LoginAPI.as_view(), name='login'),
    path('logout/', knox_views.LogoutView.as_view(), name='logout'),
    path('register/', api.RegisterAPI.as_view(), name='register'),
]