from django.urls import path
from user import api


app_name = 'user'

urlpatterns = [
    path('currentuser/', api.CurrentUser.as_view(), name='curr_user'),
    path('<uuid:uuid>/', api.UserDetail.as_view(), name='user_detail'),
    path('follow/<uuid:pk>/', api.FollowAPI.as_view(), name='follow'),
    path('search/<str:phrase>/', api.UserSearch.as_view(), name='search_users'),
]