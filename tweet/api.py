from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from tweet.serializer import TweetSerializer
from rest_framework import status
from rest_framework.response import Response
from itertools import chain
from operator import attrgetter

class UserTweets(ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TweetSerializer
    queryset = ''

    def list(self, request, *args, **kwargs):
        user_posts = request.user.tweets.all()
        user_shared_posts = request.user.share_connector_account.all()

        result_list = sorted(
            chain(user_posts, user_shared_posts),
            key=attrgetter('created'),
            reverse=True
        )

        for index in range(len(result_list)):
            print(result_list[index].created)
            if hasattr(result_list[index], 'tweet'):
                result_list[index] = result_list[index].tweet

        serializer = self.get_serializer(result_list, many=True,
                                         context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

