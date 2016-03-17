#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import os

from flask import current_app
from flask.ext.assets import ManageAssets
from flask.ext.script import (
    Manager,
    Server,
    Command,
    Option,
    Shell,
    prompt,
    prompt_pass
)
from flask.ext.security.utils import (
    encrypt_password
)

from application.competency.models import (
    Behaviour,
    Competency,
    CompetencyCluster,
    Level
)
from application.extensions import user_datastore
from application.factory import create_app
from application.models import (
    Entry,
    Link,
    LogEntry,
    Role,
    Tag,
    User
)


manager = Manager(create_app)
manager.add_option('-c', '--config', dest='config', required=False)
manager.add_command('assets', ManageAssets())
manager.add_command('runserver', Server(
    host='0.0.0.0',
    port=int(os.environ.get('PORT', '8000'))))


def _make_context():
    return dict(
        app=current_app,
        Entry=Entry,
        Link=Link,
        LogEntry=LogEntry,
        Role=Role,
        Tag=Tag,
        User=User)

manager.add_command('shell', Shell(make_context=_make_context))


class CreateUser(Command):
    """
    Creates a user for this app
    """

    def create_auth0_user(self, name, email, pwd):
        return requests.post(
            AUTH0_API_URL,
            headers={
                'Authorization': 'Bearer {token}'.format(AUTH0_CREATE_USER_JWT),
                'Content-Type': 'application/json'},
            json={
                'username': name,
                'email': email,
                'password': pwd})

    def create_app_user(self, name, email):
        return User.objects.create(
            full_name=name,
            email=email)

    def run(self):
        email = prompt('email')
        full_name = prompt('full name')
        password = prompt_pass('password')

        if not User.objects.filter(email=email):
            self.create_auth0_user(full_name, email, password)
            user = self.create_app_user(full_name, email)

            user_role = user_datastore.find_or_create_role('USER')
            user_datastore.add_role_to_user(user, user_role)

            user.update(
                inbox_email="{username}@{domain}".format(
                    username=email.split('@')[0],
                    domain=current_app.config.get('EMAIL_DOMAIN')))

        else:
            print("User with email:", email, "already exists")


class CreateXgsUsersCommand(Command):
    """
    Adds the users found in users.txt
    """

    def run(self):
        password = 'password'  # toy password for all users for now
        with open('./users.txt') as users_file:
            users = users_file.readlines()
            for user_details in users:
                email, name = user_details.strip().split(',')
                user = User.objects.filter(email=email).first()
                if not user:
                    print("No user found for email:", email, "so create")
                    user = user_datastore.create_user(
                        email=email,
                        password=encrypt_password(password),
                        full_name=name)
                    admin_role = user_datastore.find_or_create_role('ADMIN')
                    user_datastore.add_role_to_user(user, admin_role)
                    email_domain = current_app.config.get('EMAIL_DOMAIN')
                    user_name = email.split('@')[0]
                    user.inbox_email = "%s@%s" % (user_name, email_domain)
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


class EraseDatabase(Command):
    """
    Erase all data from the database
    """

    def run(self):
        self.erase_db()

    def erase_db(self):
        Behaviour.objects.delete()
        Competency.objects.delete()
        CompetencyCluster.objects.delete()
        Entry.objects.delete()
        Level.objects.delete()
        Link.objects.delete()
        LogEntry.objects.delete()
        Role.objects.delete()
        Tag.objects.delete()
        User.objects.delete()


class LoadCompetencyData(Command):
    """
    Creates compentency framework data found in csv files
    """

    def run(self):
        self.load_levels()
        self.load_competency_clusters()
        self.load_competencies()
        self.load_behaviours()

    def load_model_fixtures(self, csvfile, Model, fn=None):
        with open('./fixtures/competencies/{}'.format(csvfile)) as f:
            for row in csv.DictReader(f):
                if fn:
                    row = fn(row)
                if not Model.objects.filter(**row):
                    Model.objects.create(**row)

    def load_levels(self):
        self.load_model_fixtures('level.csv', Level)

    def load_competency_clusters(self):
        self.load_model_fixtures('competency_cluster.csv', CompetencyCluster)

    def load_competencies(self):

        def add_refs(data):
            data['cluster'] = CompetencyCluster.objects.get(
                cluster_id=data.pop('cluster_id'))
            return data

        self.load_model_fixtures('competency.csv', Competency, add_refs)

    def load_behaviours(self):

        def add_refs(data):
            data['competency'] = Competency.objects.get(
                competency_id=data.pop('competency_id'))
            data['level'] = Level.objects.get(
                level_id=data.pop('level_id'))
            return data

        self.load_model_fixtures('behaviour.csv', Behaviour, add_refs)


class FakeIdp(Command):
    """
    Run a Django OIDC IdP server application
    """

    option_list = (
        Option('--port', '-p', dest='port', required=True),
        Option('--name', '-n', dest='name', required=True),
    )

    def run(self, port, name):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'idp.settings')
        os.environ['PORT'] = port
        os.environ['APP_NAME'] = name
        from django.utils.text import slugify
        slug = slugify(os.environ['APP_NAME'])
        os.environ['DATABASE'] = slug
        os.environ['APP_IMAGE'] = '/static/images/{}.png'.format(slug)
        import django
        django.setup()
        from django.core.management import call_command
        call_command('migrate')
        from django.contrib.auth.models import User
        if len(User.objects.filter(is_superuser=True)) < 1:
            call_command('createsuperuser')
            call_command('creatersakey')
        call_command('runserver', os.environ['PORT'])


manager.add_command('create-user', CreateUser())
manager.add_command('make-user-admin', MakeUserAdminCommand())
manager.add_command('create-xgs-users', CreateXgsUsersCommand())

manager.add_command('load-competency-data', LoadCompetencyData())
manager.add_command('erase-db', EraseDatabase())

manager.add_command('fake-idp', FakeIdp())

if __name__ == '__main__':
    manager.run()
