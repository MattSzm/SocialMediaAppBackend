from rest_framework.generics import ListAPIView, CreateAPIView, ListCreateAPIView
from rest_framework import permissions
from tweet.serializer import TweetSerializer, TweetCommentSerializer
from rest_framework import status
from rest_framework.response import Response
from itertools import chain
from operator import attrgetter
from user.models import User
from tweet.models import Tweet
from django.http import Http404


class UserTweets(ListAPIView):
    serializer_class = TweetSerializer
    queryset = ''

    def get_user(self, uuid_user):
        try:
            return User.objects.get(uuid=uuid_user)
        except User.DoesNotExist:
            raise Http404

    def list(self, request, *args, **kwargs):
        found_user = self.get_user(kwargs['pk'])
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


class CreateTweet(CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TweetSerializer
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


class TweetComments(ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TweetCommentSerializer
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



