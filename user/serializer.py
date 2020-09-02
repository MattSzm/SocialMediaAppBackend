from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    number_following = serializers.ReadOnlyField(source='num_of_following')
    number_followers = serializers.ReadOnlyField(source='num_of_followers')

    class Meta:
        model = User
        fields = ('id', 'uuid', 'username', 'username_displayed',
                  'photo', 'number_following', 'number_followers')


class UserEditSerializer(serializers.ModelSerializer):
    username_readonly = serializers.ReadOnlyField(source='username')

    class Meta:
        model = User
        fields = ('id', 'uuid', 'username_readonly',
                  'username_displayed', 'photo')

