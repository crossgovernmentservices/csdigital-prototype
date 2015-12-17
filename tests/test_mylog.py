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
    user = user_datastore.create_user(email='someone@email.com',
                               password='password')

    assert user.inbox_email == 'someone@mylog.civilservice.digital'

    user_datastore.create_user(email='someone_else@email.com',
                               password='password')
    login()


def teardown():
    LogEntry.objects.delete()
    Entry.objects.delete()
    User.objects.delete()


def test_add_to_mylog():
    rv = client.get('/my-log')
    assert rv.status_code == 200
    page = BeautifulSoup(rv.data.decode('utf-8'), 'html.parser')
    assert page.h1.string == 'My log'
    assert not page.tbody.find('tr')

    rv = client.post('/my-log/entry', data=dict(content='test content 1',
                                                tags=['test tag 1']),
                     follow_redirects=True)

    assert rv.status_code == 200
    rv = client.post('/my-log/entry', data=dict(content='test content 2',
                                                tags=['test tag 2']),
                     follow_redirects=True)

    assert rv.status_code == 200

    page = BeautifulSoup(rv.data.decode('utf-8'), 'html.parser')
    assert page.h1.string == 'My log'
    log_entries = page.tbody.find_all('tr')
    assert len(log_entries) == 2


@mock.patch('application.mylog.views._verified', return_value=True)
def test_email_to_my_Log(mock_verified):

    data = {'sender': 'someone_else@email.com',
            'recipient': 'someone@mylog.civilservice.digital',
            'subject': 'the subject',
            'body-plain': 'the body of the email'}

    rv = client.post('/my-log/inbox', data=data, follow_redirects=True)

    assert rv.status_code == 200
    assert mock_verified.called

    saved = LogEntry.objects.first()
    assert saved
    assert saved.entry.content == 'the subject\nthe body of the email'
    assert saved.entry_from == 'someone_else@email.com'
    assert saved.tags
    assert saved.tags[0].name == 'Email'

