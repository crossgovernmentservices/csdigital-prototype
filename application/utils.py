import datetime

from flask import abort
from mongoengine.errors import DoesNotExist


def a_year_from_now():
    a_year_from_now = datetime.timedelta(weeks=52)
    now = datetime.datetime.utcnow()
    return now + a_year_from_now


def get_or_404(model_or_queryset, **kwargs):
    try:
        return model_or_queryset.objects.get(**kwargs)

    except AttributeError:

        try:
            return model_or_queryset.get(**kwargs)

        except DoesNotExist:
            abort(404)

    except DoesNotExist:
        abort(404)
