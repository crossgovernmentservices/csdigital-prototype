import os
import pytest

from pymongo import MongoClient

from mongoengine import connect
from mongoengine.errors import ValidationError

from application.models import Entry, LogEntry

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/xgs-test')

connect(host=MONGO_URI)


def teardown():
    client = MongoClient(MONGO_URI)
    client.drop_database(client.get_default_database())


def setup():
    os.environ['SETTINGS'] = 'application.config.TestConfig'


def test_objective_with_valid_fields():
    entry = Entry()
    entry.how = 'this is how'
    entry.what = 'this is what'
    entry.save()

    log_entry = LogEntry()
    log_entry.entry_type = 'objective'
    log_entry.entry = entry
    log_entry.save()


def test_objective_with_invalid_fields():
    entry = Entry()
    entry.how = 'this is how'
    entry.what = 'this is what'
    entry.something_not_right = 'this is not right'

    with pytest.raises(ValidationError):
        log_entry = LogEntry()
        log_entry.entry_type = 'objective'
        log_entry.entry = entry
        log_entry.save()


def test_entry_type_must_be_in_models_schema():
    entry = Entry()
    entry.save()
    log_entry = LogEntry()
    log_entry.entry_type = 'catfish'
    log_entry.entry = entry

    with pytest.raises(ValidationError):
        log_entry.save()
