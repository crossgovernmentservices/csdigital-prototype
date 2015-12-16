import pytest

from pymongo import MongoClient

from mongoengine import connect
from mongoengine.errors import ValidationError
connect('xgs-test')

from application.models import Entry


def teardown():
    mongo_uri = 'mongodb://localhost:27017/xgs-test'
    client = MongoClient(mongo_uri)
    client.drop_database('xgs-test')


def setup():
    import os
    os.environ['SETTINGS'] = 'application.config.TestConfig'


def test_feedback_with_valid_fields():
    entry = Entry()
    entry.entry_type = 'feedback'
    entry.requested_from = 'someone@email.com'
    entry.requested_by = 'anotherone@email.com'
    entry.details = 'details'
    entry.share_objectives = True
    entry.sent = True
    entry.replied = True
    entry.save()


def test_feedback_with_invalid_fields():
    entry = Entry()
    entry.entry_type = 'objective'
    entry.yikes = 'not good!'

    with pytest.raises(ValidationError):
        entry.save()
