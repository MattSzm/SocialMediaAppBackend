from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    number_following = serializers.ReadOnlyField(source='num_of_following')
    number_followers = serializers.ReadOnlyField(source='num_of_followers')
    number_of_tweets = serializers.ReadOnlyField(source='num_of_tweets')
    followed_by_current_user = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'uuid', 'username', 'username_displayed',
                  'photo', 'number_following', 'number_followers',
                  'number_of_tweets', 'followed_by_current_user')

    def get_followed_by_current_user(self, obj):
        if not self.context['request'].user.is_anonymous:
            if obj in self.context['request'].user.following.all():
                return True
        return False


class UserEditSerializer(serializers.ModelSerializer):
    number_of_tweets = serializers.ReadOnlyField(source='num_of_tweets')
    number_following = serializers.ReadOnlyField(source='num_of_following')
    number_followers = serializers.ReadOnlyField(source='num_of_followers')

    class Meta:
        model = User
        fields = ('id', 'uuid', 'username',
                  'username_displayed', 'photo',
                  'number_following', 'number_followers',
                  'number_of_tweets')
        read_only_fields = ('username',)

