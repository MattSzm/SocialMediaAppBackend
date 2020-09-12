from rest_framework import serializers
from user.models import User
from django.contrib.auth import authenticate

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


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'username_displayed',
                  'photo', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def validate(self, data):
        if len(data['password']) < 6:
            raise serializers.ValidationError("Password too short")
        if ' ' in data['username']:
            raise serializers.ValidationError("Username cannot contain whitespaces")
        if '@' not in data['email']:
            raise serializers.ValidationError("Invalid email")
        return data
