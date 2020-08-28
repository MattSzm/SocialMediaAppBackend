from rest_framework.generics import RetrieveAPIView, GenericAPIView, RetrieveUpdateDestroyAPIView
from user import serializer
from user import models
from rest_framework.response import Response
from knox.models import AuthToken
from rest_framework import permissions


class UserDetail(RetrieveAPIView):
    serializer_class = serializer.UserSerializer
    lookup_field = 'uuid'

    def get_queryset(self):
        return models.User.objects.all()


class LoginAPI(GenericAPIView):
    serializer_class = serializer.LoginSerializer

    def post(self, request, format=None):
        serializer_object = self.get_serializer(data=request.data)
        serializer_object.is_valid(raise_exception=True)
        user = serializer_object.validated_data
        return Response({
            "user": serializer.UserSerializer(user,
                                context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]})


class RegisterAPI(GenericAPIView):
    serializer_class = serializer.RegisterSerializer

    def post(self, request, format=None):
        serializer_object = self.get_serializer(data=request.data)
        serializer_object.is_valid(raise_exception=True)
        user = serializer_object.save()
        return Response({
            "user": serializer.UserSerializer(user,
                                              context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]})


class CurrentUser(RetrieveUpdateDestroyAPIView):
    serializer_class = serializer.UserEditSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


