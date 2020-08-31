from django.urls import path
from user import api
from knox import views as knox_views


app_name = 'user'

urlpatterns = [
    path('login/', api.LoginAPI.as_view(), name='login'),
    path('logout/', knox_views.LogoutView.as_view(), name='logout'),
    path('register/', api.RegisterAPI.as_view(), name='register'),
    path('currentuser/', api.CurrentUser.as_view(), name='curr_user'),
    path('<uuid:uuid>/', api.UserDetail.as_view(), name='user_detail'),
    path('follow/<uuid:pk>/', api.FollowAPI.as_view(), name='follow'),
    path('search/<str:phrase>/', api.UserSearch.as_view(), name='search_users'),
]