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
