import datetime

from flask import abort


def a_year_from_now():
    a_year_from_now = datetime.timedelta(weeks=52)
    now = datetime.datetime.utcnow()
    return now + a_year_from_now


def get_or_404(cls, **kwargs):
    try:
        return cls.objects.get(**kwargs)

    except cls.DoesNotExist:
        abort(404)
