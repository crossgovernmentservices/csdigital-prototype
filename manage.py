#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import os

from flask.ext.script import (
    Manager,
    Server,
    Command,
    prompt,
    prompt_pass
)

from flask.ext.security.utils import (
    encrypt_password
)

from application.models import (
    Entry,
    Link,
    LogEntry,
    Role,
    Tag,
    User
)
from application.competency.models import (
    Behaviour,
    Competency,
    CompetencyCluster,
    Level
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
            user = user_datastore.create_user(
                email=email,
                password=encrypt_password(password),
                full_name=full_name)
            user_role = user_datastore.find_or_create_role('USER')
            user_datastore.add_role_to_user(user, user_role)
            email_domain = app.config.get('EMAIL_DOMAIN')
            user_name = email.split('@')[0]
            user.inbox_email = "%s@%s" % (user_name, email_domain)
            user.save()
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
                    email_domain = app.config.get('EMAIL_DOMAIN')
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

    def load_model_fixtures(self, csvfile, model_exists, create_model):
        with open('./fixtures/competencies/{}'.format(csvfile)) as f:
            for row in csv.DictReader(f):
                if not model_exists(row):
                    create_model(row)

    def load_levels(self):

        def exists(data):
            return Level.objects.filter(level_id=data['level_id']).count() > 0

        def create(data):
            level = Level()
            level.description = data['level_description']
            level.level_id = data['level_id']
            level.save()

        self.load_model_fixtures('level.csv', exists, create)

    def load_competency_clusters(self):

        def exists(data):
            return CompetencyCluster.objects.filter(
                cluster_id=data['competency_cluster_id']).count() > 0

        def create(data):
            cluster = CompetencyCluster()
            cluster.name = data['competency_cluster_name']
            cluster.goal = data['competency_cluster_goal']
            cluster.cluster_id = data['competency_cluster_id']
            cluster.save()

        self.load_model_fixtures('competency_cluster.csv', exists, create)

    def load_competencies(self):

        def exists(data):
            return Competency.objects.filter(
                competency_id=data['competency_id']).count() > 0

        def create(data):
            competency = Competency()
            competency.competency_id = data['competency_id']
            competency.name = data['competency_name']
            competency.overview = data['competency_overview_text']
            competency.cluster = CompetencyCluster.objects.filter(
                cluster_id=data['competency_cluster_id']).first()
            competency.save()

        self.load_model_fixtures('competency.csv', exists, create)

    def load_behaviours(self):

        def exists(data):
            return Behaviour.objects.filter(
                behaviour_id=data['pair_id']).count() > 0

        def create(data):
            behaviour = Behaviour()
            behaviour.effective = data['effective_behaviour']
            behaviour.ineffective = data['ineffective_behaviour']
            behaviour.competency = Competency.objects.filter(
                competency_id=data['competency_id']).first()
            behaviour.level = Level.objects.filter(
                level_id=data['level_id']).first()
            behaviour.behaviour_id = data['pair_id']
            behaviour.save()

        self.load_model_fixtures('behaviour.csv', exists, create)


manager.add_command('create-user', CreateUser())
manager.add_command('make-user-admin', MakeUserAdminCommand())
manager.add_command('create-xgs-users', CreateXgsUsersCommand())

manager.add_command('load-competency-data', LoadCompetencyData())

if __name__ == '__main__':
    manager.run()
