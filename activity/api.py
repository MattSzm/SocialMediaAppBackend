from rest_framework.generics import ListAPIView
from rest_framework import permissions

from .models import PopularUsers
from user.serializer import UserSerializer


class RecentlyPopularUsers(ListAPIView):
    serializer_class = UserSerializer
    model = PopularUsers
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = None
    """
    Endpoint returns most popular users of the last twelve hours.
    """
    def get_queryset(self):
        popular_users_object = PopularUsers.load()
        return popular_users_object.users.all()

