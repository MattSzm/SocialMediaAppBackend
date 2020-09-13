from django.urls import path

from tweet import api


app_name = 'tweet'

urlpatterns = [
    path('newsfeed/', api.NewsFeed.as_view(), name='news_feed'),
    path('byuser/<uuid:pk>/', api.UserTweets.as_view(), name='user_tweets'),
    path('create/', api.CreateTweet.as_view(), name='create_tweet'),
    path('destroy/<uuid:uuid>/', api.DestroyTweet.as_view(), name='destroy_tweet'),
    path('likes/<uuid:pk>/', api.TweetLike.as_view(), name='tweet_like'),
    path('share/<uuid:pk>/', api.TweetShare.as_view(), name='tweet_share'),
    path('comments/<uuid:pk>/', api.TweetComments.as_view(), name='tweet_comments'),
    path('search/<str:phrase>/', api.TweetSearch.as_view(), name='search_tweets'),
    path('withhashtag/<str:value>/', api.TweetsWithHashtag.as_view(),
                                            name='tweets_with_hashtag')
]