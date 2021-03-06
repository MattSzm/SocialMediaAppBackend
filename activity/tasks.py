from datetime import timedelta

from django.utils import timezone
from celery.schedules import crontab

from twitterclonebackend.celery import app
from user.models import User, ContactConnector
from .models import PopularUsers, UserHashtagTrends
from tweet.models import Hashtag, HashtagConnector, Tweet


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
            crontab(hour="*/6"),
            most_popular_users_during_the_day.s(12,3),
                name='perform_most_popular_users')

    sender.add_periodic_task(
            crontab(hour="*/6"),
            create_user_hashtags_trends.s(12, 3),
                name='perform_hashtag_trends')


@app.task
def most_popular_users_during_the_day(hours_offset, amount_of_users):
    following_actions = ContactConnector.objects.filter(
        created__gte=(timezone.now() - timedelta(
                        hours=hours_offset, minutes=0)))
    users_hashmap = {}
    for single_action in following_actions:
        followed_user_uuid = single_action.user_to.uuid
        if followed_user_uuid in users_hashmap:
            users_hashmap[followed_user_uuid] += 1
        else:
            users_hashmap[followed_user_uuid] = 1

    # #todo: testing purpose, need to be deleted!
    # if len(users_hashmap) < 3:
    #     print('not performing')
    #     return

    popular_users_objects = PopularUsers.load()
    popular_users_objects.users.clear()

    for _ in range(amount_of_users):
        current_max = 0
        uuid_of_current_max = None
        for user_uuid, value in users_hashmap.items():
            if value > current_max:
                current_max = value
                uuid_of_current_max = user_uuid
        if uuid_of_current_max is not None:
            try:
                user_with_current_max = User.objects.get(
                    uuid=uuid_of_current_max)
            except User.DoesNotExist:
                pass
            else:
                popular_users_objects.users.add(user_with_current_max)
            del users_hashmap[uuid_of_current_max]
    popular_users_objects.save()


@app.task
def create_user_hashtags_trends(hours_offset, amount_of_hashtags):
    def update_most_popular_tweet(single_trend):
        def count_value(tweet):
            return (tweet.number_of_likes + tweet.number_of_comments*1.2 +
                        tweet.number_of_shares*1.5)


        filtered_tweets = single_trend.tweets.filter(
            created__gte=(timezone.now() - timedelta(
                hours=hours_offset*3, minutes=0)))
        if filtered_tweets:
            most_popular = [filtered_tweets[0].uuid,
                            count_value(filtered_tweets[0])]
            for index in range(1, len(filtered_tweets)):
                current_tweet_value = count_value(filtered_tweets[index])
                if current_tweet_value > most_popular[1]:
                    most_popular = [filtered_tweets[index].uuid,
                                    current_tweet_value]
            try:
                most_popular_tweet = Tweet.objects.get(uuid=most_popular[0])
            except Tweet.DoesNotExist:
                pass
            else:
                single_trend.most_popular_tweet = most_popular_tweet
                single_trend.save()


    def process_hashmap_results(input_hashmap):
        output_list = []
        for _ in range(amount_of_hashtags):
            current_max = 0
            hashtag_value_of_current_max = None
            for hashtag_value, value in input_hashmap.items():
                if value > current_max:
                    current_max = value
                    hashtag_value_of_current_max = hashtag_value
            if hashtag_value_of_current_max is not None:
                try:
                    hashtag_object_of_current_max = Hashtag.objects.get(
                        hashtag_value=hashtag_value_of_current_max)
                except Hashtag.DoesNotExist:
                    pass
                else:
                    output_list.append(hashtag_object_of_current_max)
                del input_hashmap[hashtag_value_of_current_max]
        return output_list


    def create_default_trends():
        hashtag_connectors = HashtagConnector.objects.filter(
            created__gte=(timezone.now() - timedelta(
                hours=hours_offset, minutes=0)))
        hashtag_values_hashmap = {}
        for single_hashtag_connector in hashtag_connectors:
            #hashtag values are unique
            hashtag_value = single_hashtag_connector.hashtag.hashtag_value
            if hashtag_value in hashtag_values_hashmap:
                hashtag_values_hashmap[hashtag_value] += 1
            else:
                hashtag_values_hashmap[hashtag_value] = 1
        return process_hashmap_results(hashtag_values_hashmap)


    def create_user_personal_trends(user):
        user_tweets = user.tweets.filter(
            created__gte=(timezone.now() - timedelta(
                hours=hours_offset, minutes=0)))
        hashtag_values_hashmap = {}
        for single_tweet in user_tweets:
            for single_hashtag in single_tweet.related_hashtags.all():
                hashtag_value = single_hashtag.hashtag_value
                if hashtag_value not in hashtag_values_hashmap:
                    hashtag_values_hashmap[hashtag_value] = 1
                else:
                    hashtag_values_hashmap[hashtag_value] += 1
        return process_hashmap_results(hashtag_values_hashmap)


    defaults = create_default_trends()
    for default in defaults:
        update_most_popular_tweet(default)

    for single_user in User.objects.all():
        personal_trends = create_user_personal_trends(single_user)
        try:
            user_hashtag_trends_object = UserHashtagTrends.objects.get(
                user=single_user)
        except UserHashtagTrends.DoesNotExist:
            user_hashtag_trends_object = UserHashtagTrends.objects.create(
                user=single_user)
        user_hashtag_trends_object.hashtags.clear()
        for single_personal_trend in personal_trends:
            if (not single_personal_trend.most_popular_tweet or
                    single_personal_trend.last_modify < (timezone.now() -
                     timedelta(hours=hours_offset, minutes=0))):
                update_most_popular_tweet(single_personal_trend)
            user_hashtag_trends_object.hashtags.add(single_personal_trend)
        for single_default_object in defaults:
            if len(user_hashtag_trends_object.hashtags.all()) == amount_of_hashtags:
                break
            if not single_default_object in user_hashtag_trends_object.hashtags.all():
                user_hashtag_trends_object.hashtags.add(single_default_object)
        user_hashtag_trends_object.save()
