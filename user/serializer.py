from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    number_following = serializers.ReadOnlyField(source='num_of_following')
    number_followers = serializers.ReadOnlyField(source='num_of_followers')
    number_of_tweets = serializers.ReadOnlyField(source='num_of_tweets')

    class Meta:
        model = User
        fields = ('id', 'uuid', 'username', 'username_displayed',
                  'photo', 'number_following', 'number_followers',
                  'number_of_tweets')


class UserEditSerializer(serializers.ModelSerializer):

    number_following = serializers.ReadOnlyField(source='num_of_following')
    number_followers = serializers.ReadOnlyField(source='num_of_followers')

    class Meta:
        model = User
        fields = ('id', 'uuid', 'username',
                  'username_displayed', 'photo',
                  'number_following', 'number_followers')
        read_only_fields = ('username',)

