from datetime import timedelta

from django.utils import timezone

from twitterclonebackend.celery import app
from user.models import User, ContactConnector
from .models import PopularUsers

#todo: pass 4320(12 hours) in production - 10sec for testing purpose
@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10.0,
            most_popular_users_during_the_day.s(12, 3),
            name='perform_most_popular_users')


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

    #todo: testing purpose, need to be deleted!
    if len(users_hashmap) < 3:
        print('not performing')
        return

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