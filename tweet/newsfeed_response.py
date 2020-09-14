from django.utils import timezone
from django.conf import settings


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