from pymongo import MongoClient

from mongoengine import connect
connect('xgs-test')

from application.models import (
    Entry,
    LogEntry
)


def teardown():
    mongo_uri = 'mongodb://localhost:27017/xgs-test'
    client = MongoClient(mongo_uri)
    client.drop_database('xgs-test')


def setup():
    import os
    os.environ['SETTINGS'] = 'application.config.TestConfig'


def test_save_log_entry_with_content():
    entry = Entry()
    entry.content = 'content is all there is'
    entry.save()

    log_entry = LogEntry()
    log_entry.entry_type = 'log'
    log_entry.entry = entry
    log_entry.save()

    from_db = LogEntry.objects(id=log_entry.id).get()
    assert from_db.entry.content == 'content is all there is'
    assert from_db.entry_type == 'log'


def test_save_log_entry_with_feedback():
    entry = Entry()
    entry.requested_from = 'someone@email.com'
    entry.requested_by = 'anotherone@email.com'
    entry.details = 'details'
    entry.share_objectives = True
    entry.sent = True
    entry.replied = True
    entry.save()

    log_entry = LogEntry()
    log_entry.entry_type = 'feedback'
    log_entry.entry = entry
    log_entry.save()

    from_db = LogEntry.objects(id=log_entry.id).get()
    assert from_db.entry_type == 'feedback'
    assert from_db.entry.requested_from == 'someone@email.com'
    assert from_db.entry.requested_by == 'anotherone@email.com'
    assert from_db.entry.details == 'details'
    assert from_db.entry.share_objectives
    assert from_db.entry.sent
    assert from_db.entry.replied


def test_save_log_entry_with_objective():
    entry = Entry()
    entry.how = 'this is how'
    entry.what = 'this is what'
    entry.save()

    log_entry = LogEntry()
    log_entry.entry_type = 'objective'
    log_entry.entry = entry
    log_entry.save()

    from_db = LogEntry.objects(id=log_entry.id).get()
    assert from_db.entry_type == 'objective'
    assert from_db.entry.how == 'this is how'
    assert from_db.entry.what == 'this is what'
