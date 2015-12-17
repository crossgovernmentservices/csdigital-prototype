import pytest

from pymongo import MongoClient

from mongoengine import connect
from mongoengine.errors import ValidationError
connect('xgs-test')

from application.models import Entry, LogEntry


def teardown():
    mongo_uri = 'mongodb://localhost:27017/xgs-test'
    client = MongoClient(mongo_uri)
    client.drop_database('xgs-test')


def setup():
    import os
    os.environ['SETTINGS'] = 'application.config.TestConfig'


def test_log_with_valid_fields():
    entry = Entry()
    entry.content = 'content is all there is'
    entry.save()

    log_entry = LogEntry()
    log_entry.entry_type = 'log'
    log_entry.entry = entry
    entry.save()


def test_log_with_invalid_fields():
    entry = Entry()
    entry.foo = 'this is not right there is no foo'
    entry.save()

    log_entry = LogEntry()
    log_entry.entry_type = 'log'
    log_entry.entry = entry

    with pytest.raises(ValidationError):
        log_entry.save()
