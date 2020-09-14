from operator import attrgetter

from django.utils.dateparse import parse_datetime


def convert_from_string_to_date_if_needed(date):
    if type(date) == str:
        date = parse_datetime(date)
    return date

def sort_single_set(set):
    return sorted(set,
            key=attrgetter('created'),
            reverse=True)

