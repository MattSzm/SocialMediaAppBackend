from rest_framework.generics import RetrieveAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from user import serializer
from user import models
from rest_framework.response import Response
from knox.models import AuthToken


class UserDetail(RetrieveAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = serializer.UserSerializer
    lookup_field = 'uuid'

    def get_queryset(self):
        return models.User.objects.all()


class LoginView(GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = serializer.LoginSerializer

    def post(self, request, format=None):
        serializer_object = self.get_serializer(data=request.data)
        serializer_object.is_valid(raise_exception=True)
        user = serializer_object.validated_data
        return Response({
            "user": serializer.UserSerializer(user,
                                context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]})
