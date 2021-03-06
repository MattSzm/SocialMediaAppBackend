from django.db.models import Q
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status

from user import serializer
from user import models
from tweet.getters import get_user
from tweet.searching import UserSearchEngine


class UserDetailByUuid(generics.RetrieveAPIView):
    serializer_class = serializer.UserSerializer
    lookup_field = 'uuid'
    """
    Returns user detail data.
    Need to be passed user's uuid in the url.
    """

    def get_queryset(self):
        return models.User.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance,
                                         context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserDetailByNickname(generics.RetrieveAPIView):
    serializer_class = serializer.UserSerializer
    lookup_field = 'username'
    """
    Returns user detail data.
    Need to be passed user's username in the url.
    Usernames are unique so there won't be a collision. 
    Should be used only when we do not have access to uuid.
    """

    def get_queryset(self):
        return models.User.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance,
                                    context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class CurrentUser(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializer.UserEditSerializer
    permission_classes = (permissions.IsAuthenticated,)
    """
    Return current user's detail data.
    With this endpoint, client can either update or delete account.
    No url's args needed.
    """
    def get_object(self):
        return self.request.user


class FollowAPI(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def check_if_exists(self, user_from, user_to):
        try:
            result = models.ContactConnector.objects.get(
                user_from=user_from,
                user_to=user_to
            )
        except models.ContactConnector.DoesNotExist:
            return False
        else:
            return result

    def post(self, request, *args, **kwargs):
        """
        Current user starts follow another user.
        Possible if there is no follow yet.
        Otherwise, server returns HTTP_208.
        Need to be passed user_to's uuid in the url.
        No (post) data needed.
        """
        user_from = request.user
        user_to = get_user(kwargs['uuid'])
        if (self.check_if_exists(user_from, user_to) or
                user_from == user_to):
            return Response(status=status.HTTP_409_CONFLICT)
        models.ContactConnector.objects.create(
            user_from=user_from,
            user_to=user_to
        )
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        """
        Deleting follow.
        Current user is no more following user
        whose uuid is passed in url.
        If request is invalid, because there is no follow,
        server returns HTTP_406.
        """
        user_from = request.user
        user_to = get_user(kwargs['uuid'])
        found_follow = self.check_if_exists(user_from, user_to)
        if not found_follow:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        found_follow.delete()
        return Response(status=status.HTTP_200_OK)


class UserFollowing(generics.ListAPIView):
    serializer_class = serializer.UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ''

    def list(self, request, *args, **kwargs):
        """
        Returns a list of users being followed by the user
        whose uuid was passed as a parameter.
        Client has to be authenticated.
        """
        found_user = get_user(kwargs['uuid'])
        following_users = found_user.following.all()
        if following_users:
            page = self.paginate_queryset(following_users)
            serializer = self.get_serializer(page, many=True,
                                    context={'request': request})
            return self.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserFollowers(generics.ListAPIView):
    serializer_class = serializer.UserSerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ''

    def list(self, request, *args, **kwargs):
        """
        Returns a list of users that follow the user
        whose uuid was passed as a parameter.
        Client has to be authenticated.
        """
        found_user = get_user(kwargs['uuid'])
        following_users = found_user.followers.all()
        if following_users:
            page = self.paginate_queryset(following_users)
            serializer = self.get_serializer(page, many=True,
                                    context={'request': request})
            return self.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserSearch(generics.ListAPIView):
    serializer_class = serializer.UserSerializer
    queryset = ''

    def get_users(self, phrase, current_user):
        return  models.User.objects.filter(
            (Q(username__icontains=phrase) |
             Q(username_displayed__icontains=phrase)) &
                ~Q(id=current_user.id))

    def list(self, request, *args, **kwargs):
        """
             Get method returns all users with the given
             phrase in the username or username_displayed.
             Searching phrase should be passed in the url.
             If there are no users, we return HTTP_204.
             Pagination is on.
        """
        search_engine = UserSearchEngine(kwargs['phrase'])
        found_users = search_engine.get_objects()
        if found_users:
            page = self.paginate_queryset(found_users)
            serializer = self.get_serializer(page, many=True,
                                    context={'request': request})
            return self.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_204_NO_CONTENT)
