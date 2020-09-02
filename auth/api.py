from rest_framework import generics
from . import serializer
from user.serializer import UserSerializer
from rest_framework.response import Response
from knox.models import AuthToken
from rest_framework import status
from user.models import User


class LoginAPI(generics.GenericAPIView):
    serializer_class = serializer.LoginSerializer

    def post(self, request, format=None):
        """
        Username/email and password should be passed in the request.
        Server returns current user data and active token.
        """
        serializer_object = self.get_serializer(data=request.data)
        serializer_object.is_valid(raise_exception=True)
        user = serializer_object.validated_data
        return Response({
            "user": UserSerializer(user,
                            context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]},
            status=status.HTTP_200_OK)


class RegisterAPI(generics.GenericAPIView):
    serializer_class = serializer.RegistrationSerializer

    def post(self, request, format=None):
        """
        Registration requires email, password and username.
        With CheckIfUsernameIsFree we can check username availability.
        (Username has to be unique!)
        There is no way to change username later!
        User can also pass username_displayed and photo.
        Server returns created user data and active token.
        """
        serializer_object = self.get_serializer(data=request.data)
        serializer_object.is_valid(raise_exception=True)
        user = serializer_object.save()
        return Response({
            "user": UserSerializer(user,
                            context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]},
            status=status.HTTP_201_CREATED)


class CheckIfUsernameIsFree(generics.GenericAPIView):
    def find_user(self, username):
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return False
        return True

    def get(self, *args, **kwargs):
        """
        Helper endpoint checks if user with a given username exists.
        """
        wanted_username = kwargs['username']
        if self.find_user(wanted_username):
            return Response({'exists': True},
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response({'exists': False},
                        status=status.HTTP_200_OK)
