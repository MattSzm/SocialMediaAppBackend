from django.urls import path

from user import api


app_name = 'user'

urlpatterns = [
    path('currentuser/', api.CurrentUser.as_view(), name='curr_user'),
    path('uuid/<uuid:uuid>/', api.UserDetailByUuid.as_view(), name='user_detail_uuid'),
    path('username/<str:username>/', api.UserDetailByNickname.as_view(),
                                            name='user_detail_nickname'),
    path('follow/<uuid:uuid>/', api.FollowAPI.as_view(), name='follow'),
    path('followinglist/<uuid:uuid>/', api.UserFollowing.as_view(),
                    name='user_following'),
    path('followerslist/<uuid:uuid>/', api.UserFollowers.as_view(),
                    name='user_followers'),
    path('search/<str:phrase>/', api.UserSearch.as_view(), name='search_users'),
]