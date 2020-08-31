from django.http import Http404
from user.models import User
from tweet.models import Tweet, Hashtag, HashtagConnector
from django.utils.dateparse import parse_datetime
from operator import attrgetter


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


def create_related_hashtags(tweet):
    words = tweet.content.split(' ')
    for word in words:
        if word.startswith('#'):
            found_hashtag = try_to_find_hashtag(word[1:])
            if found_hashtag:
                create_hashtag_connector(found_hashtag, tweet)
            else:
                new_hashtag = Hashtag.objects.create(hashtag_value=word[1:])
                create_hashtag_connector(new_hashtag, tweet)

def try_to_find_hashtag(word):
    try:
        return Hashtag.objects.get(hashtag_value=word)
    except Hashtag.DoesNotExist:
        return False

def create_hashtag_connector(hashtag, tweet):
    HashtagConnector.objects.create(
        hashtag=hashtag,
        tweet=tweet
    )