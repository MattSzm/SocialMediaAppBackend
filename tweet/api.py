from itertools import chain
from operator import attrgetter
from collections import namedtuple

from django.utils import timezone
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response

from tweet import serializer
from tweet.models import Tweet, LikeConnector, ShareConnector, CommentConnector
from . import actions
from . import getters
from .tasks import create_related_hashtags
from .newsfeed_response import create_response_data
from .searching import TweetSearchEngine


class NewsFeed(generics.GenericAPIView):
    serializer_class = serializer.NewsFeedSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = ''
    NewsFeedContent = namedtuple('NewsFeedContent',
                                 ('tweets',
                                  'shares',
                                  'time_stamp'))

    def get_following_tweets(self, following_users, current_user, date_lt=None):
        if date_lt is None:
            date_lt = timezone.now()

        following_tweets = []
        date_lt = actions.convert_from_string_to_date_if_needed(date_lt)
        for user in following_users:
            user_tweets = user.tweets.filter(created__lt=date_lt)
            following_tweets.extend(user_tweets)
        following_tweets.extend(current_user.tweets.filter(created__lt=date_lt))
        return following_tweets

    def get_following_shares(self, following_users, current_user, date_lt=None):
        if date_lt is None:
            date_lt = timezone.now()

        following_shares = []
        date_lt = actions.convert_from_string_to_date_if_needed(date_lt)
        for user in following_users:
            user_shares = user.share_connector_account.filter(created__lt=date_lt)
            following_shares.extend(user_shares)
        following_shares.extend(current_user.share_connector_account\
                                .filter(created__lt=date_lt))
        return following_shares

    def get(self, request, *args, **kwargs):
        """
        Fetch newsfeed for current user. First request always with get method.
        'size_of_newsfeed' tells how many tweets should we dispatch.
        No url's args needed.
        """
        following_users = request.user.following.all()
        following_tweets = self.get_following_tweets(following_users,
                                                     request.user)
        following_tweets = actions.sort_single_set(following_tweets)

        following_shares = self.get_following_shares(following_users,
                                                     request.user)
        following_shares = actions.sort_single_set(following_shares)

        tweets_output, shares_output, time_stamp = create_response_data(
                                following_tweets, following_shares)

        news_feed = self.NewsFeedContent(
            tweets = tweets_output,
            shares = shares_output,
            time_stamp = time_stamp
        )
        serializer = self.get_serializer(news_feed,
                                         context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        Works as a loadmore method.
        Need to be passed timestamp of last displayed tweet and shared tweet.
        These timestamps are sent to the client.
        All client has to do is to pass them back.(Of course they can be
        changed if client needs)
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        following_users = request.user.following.all()
        following_tweets = self.get_following_tweets(following_users,
                                    request.user,
                                    date_lt=serializer.data['time_stamp'])
        following_tweets = actions.sort_single_set(following_tweets)

        following_shares = self.get_following_shares(following_users,
                                    request.user,
                                    date_lt=serializer.data['time_stamp'])
        following_shares = actions.sort_single_set(following_shares)

        tweets_output, shares_output, time_stamp = create_response_data(
                                following_tweets, following_shares)

        news_feed = self.NewsFeedContent(
            tweets=tweets_output,
            shares=shares_output,
            time_stamp = time_stamp
        )
        serializer = self.get_serializer(news_feed,
                                         context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserTweets(generics.ListAPIView):
    serializer_class = serializer.TweetSerializer
    queryset = ''

    def list(self, request, *args, **kwargs):
        """
        Return list of user's tweets.
        Need to be passed uuid of the user.
        Pagination is on.
        """
        found_user = getters.get_user(kwargs['uuid'])
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

        if result_list:
            page = self.paginate_queryset(result_list)
            serializer = self.get_serializer(page, many=True,
                                            context={'request': request})
            return self.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TweetDetail(generics.RetrieveAPIView):
    serializer_class = serializer.TweetSerializer
    lookup_field = 'uuid'

    def get_queryset(self):
        return Tweet.objects.all()

    def retrieve(self, request, *args, **kwargs):
        """
        Get method returns details of a single tweet.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance,
                                         context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateTweet(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializer.TweetSerializer
    queryset = ''

    def create(self, request, *args, **kwargs):
        """
        Post method creates new tweet.
        Need to be passed: content and image(alternatively)
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
        new_tweet = serializer.save(user=self.request.user)
        create_related_hashtags.delay(new_tweet.id)


class DestroyTweet(generics.DestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'uuid'
    """
    Destroys tweet with a given uuid.
    """

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

    def check_permissions(self, request):
        if request.method in permissions.SAFE_METHODS:
            return True
        super(TweetComments, self).check_permissions(request)

    def dispatch(self, request, *args, **kwargs):
        self.found_tweet = getters.get_tweet(kwargs['uuid'])
        return super(TweetComments, self).dispatch(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        Show comments of given tweet.
        Need to be passed uuid of the tweet.
        Pagination is on.
        """
        tweet_comments = self.found_tweet.comment_connector_tweet.all()
        if tweet_comments:
            page = self.paginate_queryset(tweet_comments)
            serializer = self.get_serializer(page, many=True,
                                            context={'request': request})
            return self.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def create(self, request, *args, **kwargs):
        """
        Create new comment to the tweet as a current
        authenticated user.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
        serializer.save(account=self.request.user,
                        tweet=self.found_tweet)


class DestroyTweetComment(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def check_if_exists(self, request, found_tweet, comment_id):
        try:
            result = CommentConnector.objects.get(
                account=request.user,
                tweet=found_tweet,
                id=comment_id
            )
        except CommentConnector.DoesNotExist:
            return False
        else:
            return result

    def delete(self, request, *args, **kwargs):
        """
            Destroys comment with a given uuid.
        """
        found_tweet = getters.get_tweet(kwargs['tweetuuid'])
        found_comment = self.check_if_exists(request,
                        found_tweet, kwargs['commentid'])
        if not found_comment:
            return Response(status=status.HTTP_404_NOT_FOUND)
        found_comment.delete()
        return Response(status=status.HTTP_200_OK)


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
        else:
            return result

    def post(self, request, *args, **kwargs):
        """
        Create new tweet's like.
        Only if current user hasn't liked the tweet before.
        Otherwise, we return HTTP_208.
        Need to be passed tweet's uuid in the url.
        No (post) data needed.
        """
        found_tweet = getters.get_tweet(kwargs['uuid'])
        if self.check_if_exists(request, found_tweet):
            return Response(status=status.HTTP_409_CONFLICT)
        created_like = LikeConnector.objects.create(
            account=request.user,
            tweet=found_tweet
        )
        if created_like:
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        """
        If possible, delete tweet's like of the current user.
        Otherwise, we cannot perform request and return HTTP_406
        """
        found_tweet = getters.get_tweet(kwargs['uuid'])
        found_like = self.check_if_exists(request, found_tweet)
        if not found_like:
            return Response(status=status.HTTP_404_NOT_FOUND)
        found_like.delete()
        return Response(status=status.HTTP_200_OK)


class TweetShare(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializer.ShareSerializer

    def check_if_exists(self, request, found_tweet):
        try:
            result = ShareConnector.objects.get(
                account=request.user,
                tweet=found_tweet
            )
        except ShareConnector.DoesNotExist:
            return False
        else:
            return result

    def post(self, request, *args, **kwargs):
        """
        Create new tweet's share.
        Only if current user hasn't shared the tweet before.
        User can share post ONLY ONCE.
        Otherwise, we return HTTP_208.
        Need to be passed tweet's uuid in the url.
        No (post) data needed.
        """
        found_tweet = getters.get_tweet(kwargs['uuid'])
        if self.check_if_exists(request, found_tweet):
            return Response(status=status.HTTP_409_CONFLICT)
        if request.user != found_tweet.user:
            created_share = ShareConnector.objects.create(
                account=request.user,
                tweet=found_tweet
            )
            if created_share:
                serializer = self.get_serializer(created_share,
                                        context={'request': request})
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)

    def delete(self, request, *args, **kwargs):
        """
        If possible, delete tweet's share of the current user.
        Otherwise, we cannot perform request and return HTTP_406
        """
        found_tweet = getters.get_tweet(kwargs['uuid'])
        found_share = self.check_if_exists(request, found_tweet)
        if not found_share:
            return Response(status=status.HTTP_404_NOT_FOUND)
        found_share.delete()
        return Response(status=status.HTTP_200_OK)


class TweetSearch(generics.ListAPIView):
    serializer_class = serializer.TweetSerializer
    queryset = ''

    def list(self, request, *args, **kwargs):
        """
        Get method returns all tweets with the given
        phrase in their contents.
        Searching phrase should be passed in the url.
        If there is no tweets, we return HTTP_204.
        Pagination is on.
        """
        search_engine = TweetSearchEngine(kwargs['phrase'])
        found_tweets = search_engine.get_objects()
        if found_tweets:
            page = self.paginate_queryset(found_tweets)
            serializer = self.get_serializer(page, many=True,
                                    context={'request': request})
            return self.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_204_NO_CONTENT)


class TweetsWithHashtag(generics.ListAPIView):
    serializer_class = serializer.TweetSerializer
    queryset = ''

    def list(self, request, *args, **kwargs):
        """
        Get method returns all tweets with the given
        hashtag in their contents.
        The hashtag value should be passed in the url.
        If there is no tweets, we return HTTP_204.
        Pagination is on.
        """
        hashtag_object = getters.get_hashtag(kwargs['value'])
        related_tweets = hashtag_object.tweets.all()
        if related_tweets:
            page = self.paginate_queryset(related_tweets)
            serializer = self.get_serializer(page, many=True,
                                    context={'request': request})
            return self.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_204_NO_CONTENT)