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


def test_objective_with_valid_fields():
    entry = Entry()
    entry.entry_type = 'objective'
    entry.how = 'this is how'
    entry.what = 'this is what'
    entry.save()


def test_objective_with_invalid_fields():
    entry = Entry()
    entry.entry_type = 'objective'
    entry.how = 'this is how'
    entry.what = 'this is what'
    entry.something_not_right = 'this is not right'

    with pytest.raises(ValidationError):
        entry.save()


def test_entry_requires_type_field():
    entry = Entry()
    entry.entry_type = None
    with pytest.raises(ValidationError):
        entry.save()


def test_entry_type_must_be_in_models_schema():
    entry = Entry()
    entry.entry_type = 'catfish'
    with pytest.raises(ValidationError):
        entry.save()
