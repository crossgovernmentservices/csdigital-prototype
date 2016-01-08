import os
import mock
import unittest

from bs4 import BeautifulSoup
from mongoengine import connect

from application.extensions import user_datastore
from application.factory import create_app
from application.models import (
    Entry,
    LogEntry,
    User
)

MONGO_URI = os.environ.get('MONGO_TEST_URI',
                           'mongodb://localhost:27017/xgs-test')

connect(host=MONGO_URI)


@unittest.skip('need to mock AWS')
class TestFeedback(unittest.TestCase):

    def login(self, email):
        return self.client.post(
            '/login',
            data={
                'email': email,
                'password': 'password'},
            follow_redirects=True)

    def logout(self):
        return self.client.get('/logout', follow_redirects=True)

    def setup(self):
        app = create_app('application.config.TestConfig')
        self.client = app.test_client()

        user_datastore.create_user(email='someone@email.com',
                                   password='password')
        user_datastore.create_user(email='someone_else@email.com',
                                   password='password')

    def teardown(self):
        LogEntry.objects.delete()
        Entry.objects.delete()
        User.objects.delete()
        self.logout()

    @mock.patch('application.feedback.views._send_feedback_email')
    def test_request_feedback(self, mock_send_feedback_email):

        self.login('someone@email.com')

        data = {'share-objectives': 'share-objectives',
                'email': ['someone_else@email.com'],
                'feedback-template': 'this is a test template'
                }

        rv = self.client.post('/get-feedback', data=data)

        assert rv.status_code == 200
        assert mock_send_feedback_email.called

        saved = LogEntry.objects.first()
        from_user = User.objects.filter(email='someone@email.com').first()
        to_user = User.objects.filter(email='someone_else@email.com').first()

        assert saved
        assert saved.entry_type == 'feedback'
        assert saved.entry.requested_by == from_user.email
        assert saved.entry.requested_from == to_user.email
        assert saved.entry.template == 'this is a test template'

    @mock.patch('application.feedback.views._send_feedback_email')
    def test_view_feedback_requests(self, mock_send_feedback_email):

        # make sure no one has asked for feedback
        self.login('someone_else@email.com')
        rv = self.client.get('/give-feedback')
        assert rv.status_code == 200
        page = BeautifulSoup(rv.data.decode('utf-8'), 'html.parser')
        assert page.h1.string == "Feedback you've sent about colleagues"
        feedback_requests = page.tbody.find_all('tr')
        assert len(feedback_requests) == 0
        self.logout()

        # another person asks for feeback
        self.login('someone@email.com')
        data = {'email': ['someone_else@email.com'],
                'feedback-template': 'this is a test template'
                }
        rv = self.client.post('/get-feedback', data=data)
        assert rv.status_code == 200
        self.logout()

        # check again and see if feeback request recieved
        self.login('someone_else@email.com')
        rv = self.client.get('/give-feedback')
        assert rv.status_code == 200
        page = BeautifulSoup(rv.data.decode('utf-8'), 'html.parser')
        assert page.h1.string == "Feedback you've sent about colleagues"
        feedback_requests = page.tbody.find_all('tr')
        assert len(feedback_requests) == 1
