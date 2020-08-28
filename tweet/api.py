from rest_framework import generics
from rest_framework import permissions
from tweet.serializer import TweetSerializer, TweetCommentSerializer
from rest_framework import status
from rest_framework.response import Response
from itertools import chain
from operator import attrgetter
from user.models import User
from tweet.models import Tweet, LikeConnector, ShareConnector
from django.http import Http404


class UserTweets(generics.ListAPIView):
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


class DestroyTweet(generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'uuid'

    def check_object_permissions(self, request, obj):
        if obj.user == request.user:
            return super(DestroyTweet, self).check_object_permissions(request, obj)
        self.permission_denied(request, 'No permission!')

    def get_queryset(self):
        return Tweet.objects.all()


class CreateTweet(generics.CreateAPIView):
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


class TweetComments(generics.ListCreateAPIView):
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


class TweetLike(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_tweet(self, uuid_tweet):
        try:
            return Tweet.objects.get(uuid=uuid_tweet)
        except Tweet.DoesNotExist:
            raise Http404

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
        found_tweet = self.get_tweet(kwargs['pk'])
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
        found_tweet = self.get_tweet(kwargs['pk'])
        found_like = self.check_if_exists(request, found_tweet)
        if not found_like:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        found_like.delete()
        return Response(status=status.HTTP_200_OK)


class TweetShare(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_tweet(self, uuid_tweet):
        try:
            return Tweet.objects.get(uuid=uuid_tweet)
        except Tweet.DoesNotExist:
            raise Http404

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
        found_tweet = self.get_tweet(kwargs['pk'])
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
        found_tweet = self.get_tweet(kwargs['pk'])
        found_share = self.check_if_exists(request, found_tweet)
        if not found_share:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        found_share.delete()
        return Response(status=status.HTTP_200_OK)