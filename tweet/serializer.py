from rest_framework import serializers
from .models import Tweet

class TweetSerializer(serializers.ModelSerializer):
    number_likes = serializers.ReadOnlyField(source='number_of_likes')
    number_shares = serializers.ReadOnlyField(source='number_of_shares')
    number_comments = serializers.ReadOnlyField(source='number_of_comments')

    class Meta:
        model = Tweet
        fields = ('id', 'content', 'uuid', 'created', 'number_likes',
                  'number_shares', 'number_comments')
