from rest_framework import serializers

from .models import Tweet, CommentConnector, ShareConnector


class TweetSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.HyperlinkedRelatedField(many=False,
                                               view_name='user:user_detail_uuid',
                                               read_only=True,
                                               lookup_field='uuid')
    number_likes = serializers.ReadOnlyField(source='number_of_likes')
    number_shares = serializers.ReadOnlyField(source='number_of_shares')
    number_comments = serializers.ReadOnlyField(source='number_of_comments')
    liked_by_current_user = serializers.SerializerMethodField()

    def get_liked_by_current_user(self, obj):
        if not self.context['request'].user.is_anonymous:
            if self.context['request'].user in obj.likes.all():
                return True
        return False

    class Meta:
        model = Tweet
        fields = ('id', 'content', 'uuid', 'created', 'user', 'image',
                  'number_likes', 'number_shares', 'number_comments',
                  'liked_by_current_user')


class ShareSerializer(serializers.HyperlinkedModelSerializer):
    account = serializers.HyperlinkedRelatedField(many=False,
                                               view_name='user:user_detail_uuid',
                                               read_only=True,
                                               lookup_field='uuid')
    tweet_itself = TweetSerializer(source='tweet')

    class Meta:
        model = ShareConnector
        fields = ('id', 'account', 'created', 'tweet_itself')


class NewsFeedSerializer(serializers.Serializer):
    tweets = TweetSerializer(many=True, read_only=True)
    shares = ShareSerializer(many=True, read_only=True)
    time_stamp = serializers.DateTimeField()


class TweetCommentSerializer(serializers.HyperlinkedModelSerializer):
    account = serializers.HyperlinkedRelatedField(many=False,
                                                  view_name='user:user_detail_uuid',
                                                  read_only=True,
                                                  lookup_field='uuid')

    class Meta:
        model = CommentConnector
        fields = ('id', 'comment_content', 'created', 'account')