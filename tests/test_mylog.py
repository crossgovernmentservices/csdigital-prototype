from bs4 import BeautifulSoup

from mongoengine import connect
connect('xgs-test')

from application.extensions import user_datastore
from application.factory import create_app
from application.models import (
    Entry,
    LogEntry
)

app = create_app('application.config.TestConfig')
client = app.test_client()


def login():
    return client.post('/login', data={'email': 'someone@email.com',
                       'password': 'password'}, follow_redirects=True)


def setup():
    user_datastore.create_user(email='someone@email.com',
                               password='password')
    login()


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
