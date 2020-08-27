from django.urls import path
from user import api
from knox import views as knox_views


app_name = 'user'

urlpatterns = [
    path('login/', api.LoginView.as_view(), name='login'),
    path('<uuid:uuid>/', api.UserDetail.as_view(), name='user_detail')
]