import datetime

from flask.ext.security import (
    UserMixin,
    RoleMixin
)

from flask.ext.mongoengine import MongoEngine
from mongoengine.queryset import queryset_manager

db = MongoEngine()


def _a_year_from_now():
    a_year_from_now = datetime.timedelta(weeks=52)
    now = datetime.datetime.utcnow()
    return now + a_year_from_now


class Objective(db.Document):
    what = db.StringField()
    how = db.StringField()


class Objectives(db.Document):
    started_on = db.DateTimeField(default=datetime.datetime.utcnow)
    due_by = db.DateTimeField(default=_a_year_from_now)
    status = db.StringField(default='In progress')  # again change to enum
    objectives = db.ListField(db.ReferenceField(Objective), default=[])

    def add(self, objective):
        self.objectives.append(objective)
        self.save()

    def remove(self, objective):
        Objectives.objects(id=self.id).update_one(pull__objectives__id=objective.id)
        self.save()


class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)


class User(db.Document, UserMixin):
    email = db.StringField()
    password = db.StringField()
    active = db.BooleanField(default=True)
    confirmed_at = db.DateTimeField()
    roles = db.ListField(db.ReferenceField(Role), default=[])
    full_name = db.StringField()
    # only one objectives set (current year for the moment)
    # change this one current and list of past ones?
    objectives = db.ReferenceField(Objectives)
    other_email = db.ListField(default=[])
    _inbox_email = db.StringField()

    @property
    def inbox_email(self):
        if not self._inbox_email:
            inbox_email = "%s@mylog.civilservice.digital" % self.email.split('@')[0]
            self.inbox_email = inbox_email
        return self._inbox_email

    @inbox_email.setter
    def inbox_email(self, email):
        self._inbox_email = email
        self.save()


class FeedbackRequest(db.Document):
    requested_by = db.ReferenceField(User)
    requested_from = db.ReferenceField(User)
    feedback_details = db.StringField()
    share_objectives = db.BooleanField(default=False)
    sent = db.BooleanField(default=False)
    feedback_template = db.StringField()


class Tag(db.Document):
    owner = db.ReferenceField(User)
    name = db.StringField()


class LogEntry(db.Document):
    created_date = db.DateTimeField(default=datetime.datetime.utcnow)
    content = db.StringField()
    owner = db.ReferenceField(User)
    tags = db.ListField(db.ReferenceField(Tag), default=[])

    def add_tag(self, name):
        name = name.strip()
        tag = Tag.objects.filter(name__iexact=name, owner=self.owner).first()
        if not tag:
            tag = Tag(name=name, owner=self.owner)
            tag.save()
        self.update(add_to_set__tags=tag)
        self.save()

    def has_tag(self, name):
        tag = Tag.objects.filter(name__iexact=name, owner=self.owner).first()
        if not tag:
            return False
        return tag in self.tags

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('-created_date')

