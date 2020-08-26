from django.db import models
import uuid
from django.contrib.auth import get_user_model


class Tweet(models.Model):
    content = models.CharField(max_length=280, blank=False)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False,
                            unique=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True,
                                   db_index=True)
    user = models.ForeignKey(get_user_model(),
                             related_name='tweets',
                             on_delete=models.CASCADE,
                             null=True,
                             blank=True)

    likes = models.ManyToManyField(get_user_model(),
                                   through='LikeConnector',
                                   related_name='liked_tweets')
    shares = models.ManyToManyField(get_user_model(),
                                    through='ShareConnector',
                                    related_name='shared_tweets')
    comments = models.ManyToManyField(get_user_model(),
                                      through='CommentConnector',
                                      related_name='commented_tweets')

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return str(self.uuid)

    @property
    def number_of_likes(self):
        return len(self.likes.all())

    @property
    def number_of_shares(self):
        return len(self.shares.all())

    @property
    def number_of_comments(self):
        return len(self.comments.all())


class LikeConnector(models.Model):
    account = models.ForeignKey(get_user_model(),
                                related_name='like_connector_account',
                                on_delete=models.CASCADE)
    tweet = models.ForeignKey(Tweet,
                              related_name='like_connector_tweet',
                              on_delete=models.CASCADE)


class ShareConnector(models.Model):
    account = models.ForeignKey(get_user_model(),
                                related_name='share_connector_account',
                                on_delete=models.CASCADE)
    tweet = models.ForeignKey(Tweet,
                              related_name='share_connector_tweet',
                              on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created',)


class CommentConnector(models.Model):
    account = models.ForeignKey(get_user_model(),
                                related_name='comment_connector_account',
                                on_delete=models.CASCADE)
    tweet = models.ForeignKey(Tweet,
                              related_name='comment_connector_tweet',
                              on_delete=models.CASCADE)
    comment_content = models.CharField(max_length=280, blank=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.comment_content
