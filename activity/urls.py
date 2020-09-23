from django.urls import path

from activity import api


app_name = 'activity'

urlpatterns = [
    path('popularusers/', api.RecentlyPopularUsers.as_view(),
                        name='popular_users')
]