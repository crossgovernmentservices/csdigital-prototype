#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import datetime

from flask.ext.script import (
    Manager,
    Server,
    Command,
    prompt,
    prompt_pass
)

from flask.ext.security import MongoEngineUserDatastore
from flask.ext.security.utils import (
    encrypt_password,
    verify_password
)

from application.models import (
    User,
    Role,
    Objectives,
    Objective,
    FeedbackRequest
)

from application import app
app.debug = True
port = os.environ.get('PORT', 8000)

manager = Manager(app)
manager.add_command('server', Server(host="0.0.0.0", port=port))

from application.extensions import user_datastore

class CreateUser(Command):
    """
        Creates a user for this app
    """
    def run(self):
        from flask_security.utils import encrypt_password
        email = prompt('email')
        full_name = prompt('full name')
        password = prompt_pass('password')
        if not User.objects.filter(email=email).first():
            user = user_datastore.create_user(email=email, password=encrypt_password(password), full_name=full_name)
            user_role = user_datastore.find_or_create_role('USER')
            user_datastore.add_role_to_user(user, user_role)
            user.objectives = Objectives()
            user.save(cascade=True)
        else:
            print("User with email:", email, "already exists")


class CreateXgsUsersCommand(Command):
    """
        Adds the users found in users.txt
    """
    def run(self):
        password = 'password' # toy password for all users for now
        with open('./users.txt') as users_file:
            users = users_file.readlines()
            for user_details in users:
                email, name = user_details.strip().split(',')
                user = User.objects.filter(email=email).first()
                if not user:
                    print("No user found for email:", email, "so create")
                    user = user_datastore.create_user(email=email, password=encrypt_password(password), full_name=name)
                    admin_role = user_datastore.find_or_create_role('ADMIN')
                    user_datastore.add_role_to_user(user, admin_role)
                    objectives = Objectives()
                    user.objectives = objectives
                    user.objectives.save()
                    user.save()

                else:
                    print("User with email:", email, "already created")


class MakeUserAdminCommand(Command):
    """
        Adds admin role to an existing user of this app
    """
    def run(self):
        email = prompt('email')
        admin_role = user_datastore.find_or_create_role('ADMIN')
        user = User.objects.filter(email=email).first()
        if not user:
            print("No user found for email:", email)
        else:
            user_datastore.add_role_to_user(user, admin_role)


class AddUserObjective(Command):
    """
        Adds one objective for user
    """
    def run(self):
        email = prompt('user email')
        user = User.objects.filter(email=email).first()
        if not user:
            print("No user found for email:", email)
            return
        user_objectives = Objectives.objects.filter(owner=user).first()
        what = prompt('what will you do')
        how = prompt('how will you do it')
        objective = Objective(what=what, how=how)
        user_objectives.add(objective)
        user_objectives.save()


class SendFeedbackRequests(Command):
    """
        Finds and sends unsent feedback requests for users
    """
    def run(self):
        from flask.ext.mail import Message
        from flask import render_template
        from application.extensions import mail

        requests = FeedbackRequest.objects.filter(sent=False).all()

        if not requests:
            print('Nothing to send')
            return

        for request in FeedbackRequest.objects.filter(sent=False):
            host = app.config['HOST']
            if 'localhost' in host:
                host = "%s:8000" % host
            url = "http://%s/give-feedback/%s" % (host, request.id)
            html = render_template('email/feedback-request.html', request=request, url=url)

            msg = Message(html=html,
                          subject="Feeback request from test",
                          sender="noreply@csdigital.notrealgov.uk",
                          recipients=[request.requested_from.email])
            try:
                mail.send(msg)
                request.sent = True
                request.save()
            except Exception as ex:
                print("We weren't able to handle your request", ex)

manager.add_command('create-user', CreateUser())
manager.add_command('make-user-admin', MakeUserAdminCommand())
manager.add_command('add-user-objective', AddUserObjective())
manager.add_command('create-xgs-users', CreateXgsUsersCommand())
manager.add_command('send-feedback-requests', SendFeedbackRequests())


if __name__ == '__main__':
    manager.run()
