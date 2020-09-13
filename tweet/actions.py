from operator import attrgetter

from django.http import Http404
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.conf import settings

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

def create_response_data(tweets, shares, date=None):
    tweets_output = []
    shares_output = []
    if not date:
        date = timezone.now()
    counter, tweets_index, shares_index = 0, 0, 0
    while (counter < settings.NEWSFEED_SIZE and
                tweets_index < len(tweets) and
                shares_index < len(shares)):
        if tweets[tweets_index].created >= shares[shares_index].created:
            tweets_output.append(tweets[tweets_index])
            date = tweets[tweets_index].created
            tweets_index += 1
        else:
            shares_output.append(shares[shares_index])
            date = shares[shares_index].created
            shares_index += 1
        counter += 1
    while (counter < settings.NEWSFEED_SIZE and
                tweets_index < len(tweets)):
        tweets_output.append(tweets[tweets_index])
        date = tweets[tweets_index].created
        tweets_index += 1
        counter += 1
    while (counter < settings.NEWSFEED_SIZE and
                shares_index < len(shares)):
        shares_output.append(shares[shares_index])
        date = shares[shares_index].created
        shares_index += 1
        counter += 1
    return tweets_output, shares_output, date

