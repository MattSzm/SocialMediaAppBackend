from rest_framework import serializers
from .models import Tweet, CommentConnector

class TweetSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(many=False,
                                               view_name='user:user_detail',
                                               read_only=True,
                                               lookup_field='uuid')
    number_likes = serializers.ReadOnlyField(source='number_of_likes')
    number_shares = serializers.ReadOnlyField(source='number_of_shares')
    number_comments = serializers.ReadOnlyField(source='number_of_comments')

    class Meta:
        model = Tweet
        fields = ('id', 'content', 'uuid', 'created', 'user', 'number_likes',
                  'number_shares', 'number_comments')


class TweetCommentSerializer(serializers.HyperlinkedModelSerializer):
    account = serializers.HyperlinkedRelatedField(many=False,
                                                  view_name='user:user_detail',
                                                  read_only=True,
                                                  lookup_field='uuid')

    class Meta:
        model = CommentConnector
        fields = ('id', 'comment_content', 'created', 'account')