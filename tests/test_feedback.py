import mock
from bs4 import BeautifulSoup

from mongoengine import connect
connect('xgs-test')

from application.extensions import user_datastore
from application.factory import create_app
from application.models import (
    Entry,
    LogEntry,
    User
)

app = create_app('application.config.TestConfig')
client = app.test_client()


def login():
    return client.post('/login', data={'email': 'someone@email.com',
                       'password': 'password'}, follow_redirects=True)


def setup():
    user_datastore.create_user(email='someone@email.com',
                               password='password')

    user_datastore.create_user(email='someone_else@email.com',
                               password='password')
    login()


def teardown():
    LogEntry.objects.delete()
    Entry.objects.delete()
    User.objects.delete()


@mock.patch('application.feedback.views._send_feedback_email')
def test_request_feedback(mock_send_feedback_email):

    data = {'share-objectives': 'share-objectives',
            'email': ['someone_else@email.com'],
            'feedback-template': 'this is a test template'
            }

    rv = client.post('/get-feedback', data=data)

    assert rv.status_code == 200
    assert mock_send_feedback_email.called

    saved = LogEntry.objects.first()
    from_user = User.objects.filter(email='someone@email.com').first()
    to_user = User.objects.filter(email='someone_else@email.com').first()

    assert saved
    assert saved.entry.entry_type == 'feedback'
    assert saved.entry.requested_by == from_user.email
    assert saved.entry.requested_from == to_user.email
    assert saved.entry.template == 'this is a test template'

