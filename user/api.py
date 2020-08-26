from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from user import serializer
from user import models


class UserDetail(RetrieveAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = serializer.UserSerializer
    lookup_field = 'uuid'

    def get_queryset(self):
        return models.User.objects.all()
