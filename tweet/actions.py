from django.http import Http404
from user.models import User
from tweet.models import Tweet

def get_user(uuid_user):
    try:
        return User.objects.get(uuid=uuid_user)
    except User.DoesNotExist:
        raise Http404


def get_tweet(uuid_tweet):
    try:
        return Tweet.objects.get(uuid=uuid_tweet)
    except Tweet.DoesNotExist:
        raise Http404