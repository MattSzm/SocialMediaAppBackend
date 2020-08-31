from twitterclonebackend.celery import app
from tweet.models import Hashtag, HashtagConnector, Tweet

@app.task
def create_related_hashtags(tweet_id):
    tweet = Tweet.objects.get(id=tweet_id)
    words = tweet.content.split(' ')
    for word in words:
        if word.startswith('#'):
            found_hashtag = try_to_find_hashtag(word[1:])
            if found_hashtag:
                create_hashtag_connector(found_hashtag, tweet)
            else:
                new_hashtag = Hashtag.objects.create(
                                    hashtag_value=word[1:])
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