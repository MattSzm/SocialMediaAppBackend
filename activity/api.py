from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework import permissions
from rest_framework import status
from rest_framework.response import Response

from .models import PopularUsers, UserHashtagTrends
from user.serializer import UserSerializer
from .serializer import HashtagTrendsSerializer


class RecentlyPopularUsers(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = None
    """
    Endpoint returns most popular users of the last twelve hours.
    """
    def get_queryset(self):
        popular_users_object = PopularUsers.load()
        return popular_users_object.users.all()


class PersonalHashtagTrends(GenericAPIView):
    serializer_class = HashtagTrendsSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ''

    def get_hashtag_trends_object(self, user):
        try:
            hashtag_trends_object = UserHashtagTrends.objects.get(
                user=user)
        except UserHashtagTrends.DoesNotExist:
            return None
        else:
            return hashtag_trends_object

    def get(self, request, *args, **kwargs):
        current_user = request.user
        hashtag_trends_object = self.get_hashtag_trends_object(
            current_user)
        if hashtag_trends_object:
            serializer = self.get_serializer(
                        hashtag_trends_object)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_204_NO_CONTENT)