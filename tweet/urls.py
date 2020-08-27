from django.urls import path
from tweet import api

app_name = 'tweet'

urlpatterns = [
    path('byuser/<uuid:pk>/', api.UserTweets.as_view(), name='user_tweets'),
    path('create/', api.CreateTweet.as_view(), name='create_tweet'),
    path('comments/<uuid:pk>/', api.TweetComments.as_view(), name='tweet_comments'),
]