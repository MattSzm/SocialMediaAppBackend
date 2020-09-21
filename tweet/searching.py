from abc import ABC, abstractmethod

from django.db.models import Q

from .models import Tweet
from user.models import User


class SearchEngine(ABC):
    def __init__(self, phrase):
        self.phrase = str(phrase)
        self.input_processing()

    def input_processing(self):
        self.phrase = ' '.join(word for word in self.phrase.split()
                               if len(word) > 1)

    def merge(self, lists, left_index, right_index):
        if left_index == right_index:
            return lists[left_index]
        elif left_index > right_index:
            return {}
        else:
            middle = (left_index + right_index) // 2
            left_side = self.merge(lists, left_index, middle)
            right_side = self.merge(lists, middle + 1, right_index)
            return left_side | right_side

    @abstractmethod
    def get_objects(self):
        pass

    def filter_objects(self, words):
        pass


class TweetSearchEngine(SearchEngine):
    def get_objects(self):
        words = self.phrase.split(' ')
        array_of_sets = list(self.filter_objects(words))
        output = self.merge(array_of_sets, 0, len(array_of_sets) - 1)
        return list(output)

    def filter_objects(self, words):
        for word in words:
            yield set(Tweet.objects.filter(content__icontains=word))


class UserSearchEngine(SearchEngine):
    def get_objects(self):
        words = self.phrase.split(' ')
        array_of_sets = list(self.filter_objects(words))
        output = self.merge(array_of_sets, 0, len(array_of_sets) - 1)
        return list(output)

    def filter_objects(self, words):
        for word in words:
            yield set(User.objects.filter(
                Q(username__icontains=word) |
                 Q(username_displayed__icontains=word)))