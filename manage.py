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
    Role
)

from application.run import app
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



manager.add_command('create-user', CreateUser())
manager.add_command('make-user-admin', MakeUserAdminCommand())
manager.add_command('create-xgs-users', CreateXgsUsersCommand())

if __name__ == '__main__':
    manager.run()
