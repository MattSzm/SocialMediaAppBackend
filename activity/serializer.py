from rest_framework import serializers

from .models import UserHashtagTrends
from tweet.serializer import HashtagSerializer


class HashtagTrendsSerializer(serializers.ModelSerializer):
    hashtags = HashtagSerializer(read_only=True, many=True)

    class Meta:
        model = UserHashtagTrends
        fields = ('hashtags',)
