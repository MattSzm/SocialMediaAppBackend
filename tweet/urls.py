from django.urls import path
from tweet import api

app_name = 'tweet'

urlpatterns = [
    path('curruser/tweets/', api.UserTweets.as_view(), name='user_tweets')
]