from django.db import models

from user.models import User
from tweet.models import Hashtag

class SingletonModel(models.Model):

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class PopularUsers(SingletonModel):
    users = models.ManyToManyField(User,
                   related_name='belongs_to_popular_users')


class UserHashtagTrends(models.Model):
    user = models.OneToOneField(User,
                     related_name='hashtag_trends',
                     on_delete=models.CASCADE)
    hashtags = models.ManyToManyField(Hashtag,
                    related_name='trends')
