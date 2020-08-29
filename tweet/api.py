from rest_framework import generics
from rest_framework import permissions
from tweet import serializer
from rest_framework import status
from rest_framework.response import Response
from itertools import chain
from operator import attrgetter
from tweet.models import Tweet, LikeConnector, ShareConnector
from django.http import Http404
from . import actions
from collections import namedtuple
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.conf import settings


class NewsFeed(generics.GenericAPIView):
    serializer_class = serializer.NewsFeedSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ''
    NewsFeedContent = namedtuple('NewsFeedContent',
                                 ('tweets', 'shares',
                                  'oldest_tweet_date',
                                  'oldest_share_tweet'))
    size_of_newsfeed = settings.NEWSFEED_SIZE

    def get_following_tweets(self, following_users, date_lt=timezone.now()):
        following_tweets = []
        date_lt = actions.convert_from_string_to_date_if_needed(date_lt)
        for user in following_users:
            user_tweets = user.tweets.filter(created__lt=date_lt)
            following_tweets.extend(user_tweets)
        return following_tweets

    def get_following_shares(self, following_users, date_lt=timezone.now()):
        following_shares = []
        date_lt = actions.convert_from_string_to_date_if_needed(date_lt)
        for user in following_users:
            user_shares = user.share_connector_account.filter(created__lt=date_lt)
            following_shares.extend(user_shares)
        return following_shares

    def get(self, request, *args, **kwargs):
        following_users = request.user.following.all()

        following_tweets = self.get_following_tweets(following_users)
        following_tweets.extend(request.user.tweets.all())
        following_tweets = actions.sort_single_set(following_tweets)

        following_tweets = following_tweets[:self.size_of_newsfeed]
        following_tweets_date = actions.return_oldest_date(
                                    following_tweets, timezone.now())

        following_shares = self.get_following_shares(following_users)
        following_shares.extend(request.user.share_connector_account.all())
        following_shares = actions.sort_single_set(following_shares)

        following_shares = following_shares[:self.size_of_newsfeed // 2]
        following_shares_date = actions.return_oldest_date(
                                    following_shares, timezone.now())

        news_feed = self.NewsFeedContent(
            tweets=following_tweets,
            shares=following_shares,
            oldest_tweet_date=following_tweets_date,
            oldest_share_tweet=following_shares_date
        )
        serializer = self.get_serializer(news_feed,
                                         context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        following_users = request.user.following.all()

        following_tweets = self.get_following_tweets(following_users,
                                        serializer.data['oldest_tweet_date'])
        following_tweets.extend(request.user.tweets.filter(
                    created__lt=parse_datetime(serializer.data['oldest_tweet_date'])))
        following_tweets = actions.sort_single_set(following_tweets)

        following_tweets = following_tweets[:self.size_of_newsfeed]
        following_tweets_date = actions.return_oldest_date(following_tweets,
                                parse_datetime(serializer.data['oldest_tweet_date']))

        following_shares = self.get_following_shares(following_users,
                                        serializer.data['oldest_share_tweet'])
        following_shares.extend(request.user.share_connector_account.filter(
                    created__lt=parse_datetime(serializer.data['oldest_share_tweet'])))
        following_shares = actions.sort_single_set(following_shares)

        following_shares = following_shares[:self.size_of_newsfeed // 2]
        following_shares_date = actions.return_oldest_date(following_shares,
                                parse_datetime(serializer.data['oldest_share_tweet']))

        news_feed = self.NewsFeedContent(
            tweets=following_tweets,
            shares=following_shares,
            oldest_tweet_date=following_tweets_date,
            oldest_share_tweet=following_shares_date
        )
        serializer = self.get_serializer(news_feed,
                                         context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserTweets(generics.ListAPIView):
    serializer_class = serializer.TweetSerializer
    queryset = ''

    def list(self, request, *args, **kwargs):
        found_user = actions.get_user(kwargs['pk'])
        user_posts = found_user.tweets.all()
        user_shared_posts = found_user.share_connector_account.all()

        result_list = sorted(
            chain(user_posts, user_shared_posts),
            key=attrgetter('created'),
            reverse=True
        )

        for index in range(len(result_list)):
            if hasattr(result_list[index], 'tweet'):
                result_list[index] = result_list[index].tweet

        if len(result_list) > 0:
            page = self.paginate_queryset(result_list)
            serializer = self.get_serializer(page, many=True,
                                            context={'request': request})
            return self.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CreateTweet(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializer.TweetSerializer
    queryset = ''

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DestroyTweet(generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'uuid'

    def check_object_permissions(self, request, obj):
        if obj.user == request.user:
            return super(DestroyTweet, self).\
                check_object_permissions(request, obj)
        self.permission_denied(request, 'No permission!')

    def get_queryset(self):
        return Tweet.objects.all()


class TweetComments(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializer.TweetCommentSerializer
    queryset = ''

    def get_tweet(self, uuid_tweet):
        try:
            return Tweet.objects.get(uuid=uuid_tweet)
        except Tweet.DoesNotExist:
            raise Http404

    def check_permissions(self, request):
        if request.method in permissions.SAFE_METHODS:
            return True
        super(TweetComments, self).check_permissions(request)

    def dispatch(self, request, *args, **kwargs):
        self.found_tweet = self.get_tweet(kwargs['pk'])
        return super(TweetComments, self).dispatch(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        tweet_comments = self.found_tweet.comment_connector_tweet.all()

        if len(tweet_comments) > 0:
            page = self.paginate_queryset(tweet_comments)
            serializer = self.get_serializer(page, many=True,
                                            context={'request': request})
            return self.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
        serializer.save(account=self.request.user,
                        tweet=self.found_tweet)


class TweetLike(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def check_if_exists(self, request, found_tweet):
        try:
            result = LikeConnector.objects.get(
                account=request.user,
                tweet=found_tweet
            )
        except LikeConnector.DoesNotExist:
            return False
        return result

    def post(self, request, *args, **kwargs):
        found_tweet = actions.get_tweet(kwargs['pk'])
        if self.check_if_exists(request, found_tweet):
            return Response(status=status.HTTP_208_ALREADY_REPORTED)
        created_like = LikeConnector.objects.create(
            account=request.user,
            tweet=found_tweet
        )
        if created_like:
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        found_tweet = actions.get_tweet(kwargs['pk'])
        found_like = self.check_if_exists(request, found_tweet)
        if not found_like:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        found_like.delete()
        return Response(status=status.HTTP_200_OK)


class TweetShare(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def check_if_exists(self, request, found_tweet):
        try:
            result = ShareConnector.objects.get(
                account=request.user,
                tweet=found_tweet
            )
        except ShareConnector.DoesNotExist:
            return False
        return result

    def post(self, request, *args, **kwargs):
        found_tweet = actions.get_tweet(kwargs['pk'])
        if self.check_if_exists(request, found_tweet):
            return Response(status=status.HTTP_208_ALREADY_REPORTED)
        created_share = ShareConnector.objects.create(
            account=request.user,
            tweet=found_tweet
        )
        if created_share:
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        found_tweet = actions.get_tweet(kwargs['pk'])
        found_share = self.check_if_exists(request, found_tweet)
        if not found_share:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        found_share.delete()
        return Response(status=status.HTTP_200_OK)

#todo: create search engine - searching in posts
#create some dump data before