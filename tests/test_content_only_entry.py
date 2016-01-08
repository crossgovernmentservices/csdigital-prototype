import os
import pytest

from pymongo import MongoClient

from mongoengine import connect
from mongoengine.errors import ValidationError

from application.models import Entry, LogEntry

MONGO_URI = os.environ.get('MONGO_TEST_URI',
                           'mongodb://localhost:27017/xgs-test')

connect(host=MONGO_URI)


def teardown():
    client = MongoClient(MONGO_URI)
    client.drop_database(client.get_default_database())


def setup():
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
