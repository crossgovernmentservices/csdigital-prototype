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
from flask.ext.security.utils import encrypt_password, verify_password

from application.models import (
    User,
    Role,
    Objectives,
    Objective
)

from application import app

app.debug = True
port = os.environ.get('PORT', 8000)

manager = Manager(app)
manager.add_command('server', Server(host="0.0.0.0", port=port))

user_datastore = app.extensions['user_datastore']

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
        else:
            print("User with email:", email, "already exists")


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


class StartObjectivesForUser(Command):
    """
        Starts objectives for current year for user
    """
    def run(self):
        email = prompt('user email')
        user = User.objects.filter(email=email).first()
        if not user:
            print("No user found for email:", email)
            return
        if not user.objectives:
            print("Already started objectives for this year. You need to add specific items now. Use add-user-objective")
            return
        user.objectives = Objectives()
        user.save(cascade=True)

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
        user_objectives.objectives.append(objective)
        objective.save()
        user_objectives.save()


manager.add_command('create-user', CreateUser())
manager.add_command('make-user-admin', MakeUserAdminCommand())
manager.add_command('start-objectives-for-user', StartObjectivesForUser())
manager.add_command('add-user-objective', AddUserObjective())


if __name__ == '__main__':
    manager.run()
