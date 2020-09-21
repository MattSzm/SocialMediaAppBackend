from .models import User


class UserSearchEngine:
    def __init__(self, phrase):
        self.phrase = str(phrase)

    def input_processing(self):
        self.phrase = ' '.join(word for word in self.phrase.split()
                               if len(word) > 1)