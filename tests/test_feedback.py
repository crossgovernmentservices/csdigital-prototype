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


def login(email):
    return client.post('/login', data={'email': email,
                       'password': 'password'}, follow_redirects=True)


def logout():
    return client.get('/logout', follow_redirects=True)


def setup():
    user_datastore.create_user(email='someone@email.com',
                               password='password')
    user_datastore.create_user(email='someone_else@email.com',
                               password='password')


def teardown():
    LogEntry.objects.delete()
    Entry.objects.delete()
    User.objects.delete()
    logout()


@mock.patch('application.feedback.views._send_feedback_email')
def test_request_feedback(mock_send_feedback_email):

    login('someone@email.com')

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


@mock.patch('application.feedback.views._send_feedback_email')
def test_view_feedback_requests(mock_send_feedback_email):

    # make sure no one has asked for feedback
    login('someone_else@email.com')
    rv = client.get('/give-feedback')
    assert rv.status_code == 200
    page = BeautifulSoup(rv.data.decode('utf-8'), 'html.parser')
    assert page.h1.string == "Feedback you've sent about colleagues"
    feedback_requests = page.tbody.find_all('tr')
    assert len(feedback_requests) == 0
    logout()

    # another person asks for feeback
    login('someone@email.com')
    data = {'email': ['someone_else@email.com'],
            'feedback-template': 'this is a test template'
            }
    rv = client.post('/get-feedback', data=data)
    assert rv.status_code == 200
    logout()

    # check again and see if feeback request recieved
    login('someone_else@email.com')
    rv = client.get('/give-feedback')
    assert rv.status_code == 200
    page = BeautifulSoup(rv.data.decode('utf-8'), 'html.parser')
    assert page.h1.string == "Feedback you've sent about colleagues"
    feedback_requests = page.tbody.find_all('tr')
    assert len(feedback_requests) == 1
