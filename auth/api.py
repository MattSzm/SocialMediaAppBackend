from rest_framework import generics
from user import serializer
from rest_framework.response import Response
from knox.models import AuthToken
from rest_framework import status


class LoginAPI(generics.GenericAPIView):
    serializer_class = serializer.LoginSerializer

    def post(self, request, format=None):
        serializer_object = self.get_serializer(data=request.data)
        serializer_object.is_valid(raise_exception=True)
        user = serializer_object.validated_data
        return Response({
            "user": serializer.UserSerializer(user,
                            context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]},
            status=status.HTTP_200_OK)


class RegisterAPI(generics.GenericAPIView):
    serializer_class = serializer.RegisterSerializer

    def post(self, request, format=None):
        serializer_object = self.get_serializer(data=request.data)
        serializer_object.is_valid(raise_exception=True)
        user = serializer_object.save()
        return Response({
            "user": serializer.UserSerializer(user,
                            context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]},
            status=status.HTTP_201_CREATED)
