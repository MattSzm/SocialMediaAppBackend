from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    number_following = serializers.ReadOnlyField(source='num_of_following')
    number_followers = serializers.ReadOnlyField(source='num_of_followers')

    class Meta:
        model = User
        fields = ('id', 'uuid', 'username', 'username_displayed',
                  'photo', 'number_following', 'number_followers')


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def check_if_email_was_used(self, data):
        if '@' in data['username']:
            return True
        return False

    def change_username_to_email(self, data):
        try:
            found_user = User.objects.get(username=data['username'])
            data['username'] = found_user.email
        except User.DoesNotExist:
            raise serializers.ValidationError("Incorrect Credentials")

    def validate(self, data):
        if not self.check_if_email_was_used(data):
            self.change_username_to_email(data)
        user = authenticate(**data)

        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")