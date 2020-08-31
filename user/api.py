from rest_framework import generics
from user import serializer
from user import models
from rest_framework.response import Response
from rest_framework import permissions
from django.http import Http404
from rest_framework import status
from django.db.models import Q


class UserDetail(generics.RetrieveAPIView):
    serializer_class = serializer.UserSerializer
    lookup_field = 'uuid'

    def get_queryset(self):
        return models.User.objects.all()


class CurrentUser(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializer.UserEditSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class FollowAPI(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_user(self, uuid_user):
        try:
            return models.User.objects.get(uuid=uuid_user)
        except models.User.DoesNotExist:
            raise Http404

    def check_if_exists(self, user_from, user_to):
        try:
            result = models.ContactConnector.objects.get(
                user_from=user_from,
                user_to=user_to
            )
        except models.ContactConnector.DoesNotExist:
            return False
        return result

    def post(self, request, *args, **kwargs):
        user_from = request.user
        user_to = self.get_user(kwargs['pk'])
        if self.check_if_exists(user_from, user_to):
            return Response(status=status.HTTP_208_ALREADY_REPORTED)
        models.ContactConnector.objects.create(
            user_from=user_from,
            user_to=user_to
        )
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        user_from = request.user
        user_to = self.get_user(kwargs['pk'])
        found_follow = self.check_if_exists(user_from, user_to)
        if not found_follow:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
        found_follow.delete()
        return Response(status=status.HTTP_200_OK)


class UserSearch(generics.ListAPIView):
    serializer_class = serializer.UserSerializer
    queryset = ''

    def get_users(self, phrase, current_user):
        return  models.User.objects.filter(
            (Q(username__icontains=phrase) |
             Q(username_displayed__icontains=phrase)) &
                ~Q(id=current_user.id))

    def list(self, request, *args, **kwargs):
        found_users = self.get_users(kwargs['phrase'], request.user)
        if len(found_users) > 0:
            page = self.paginate_queryset(found_users)
            serializer = self.get_serializer(page, many=True,
                                    context={'request': request})
            return self.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_204_NO_CONTENT)