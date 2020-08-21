from django.db import models
import uuid
from django.contrib.auth import get_user_model


class Tweet(models.Model):
    content = models.CharField(max_length=280, blank=False)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False,
                            unique=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(get_user_model(),
                                   through='LikeConnector',
                                   related_name='liked_tweets')


    def __str__(self):
        return str(self.uuid)



class LikeConnector(models.Model):
    account = models.ForeignKey(get_user_model(),
                                related_name='like_connector_account',
                                on_delete=models.CASCADE)
    tweet = models.ForeignKey(Tweet,
                              related_name='like_connector_tweet',
                              on_delete=models.CASCADE)
