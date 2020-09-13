from operator import attrgetter

from django.http import Http404
from django.utils.dateparse import parse_datetime

from user.models import User
from tweet.models import Tweet, Hashtag




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

def get_hashtag(hashtag_value):
    try:
        return Hashtag.objects.get(hashtag_value=hashtag_value)
    except Hashtag.DoesNotExist:
        raise Http404

def convert_from_string_to_date_if_needed(date):
    if type(date) == str:
        date = parse_datetime(date)
    return date

def sort_single_set(set):
    return sorted(set,
            key=attrgetter('created'),
            reverse=True)

def return_oldest_date(set, prev_date):
    for item in set:
        if item and item.created < prev_date:
            prev_date = item.created
    return prev_date
