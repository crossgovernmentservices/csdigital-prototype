import datetime

from flask.ext.security import (
    UserMixin,
    RoleMixin
)

from flask.ext.mongoengine import MongoEngine
from mongoengine.queryset import queryset_manager
from mongoengine.errors import ValidationError

db = MongoEngine()


def _a_year_from_now():
    a_year_from_now = datetime.timedelta(weeks=52)
    now = datetime.datetime.utcnow()
    return now + a_year_from_now


schemas = {'objective': ('how', 'what', 'started_on', 'due_by'),
           'feedback': ('feedback_template', 'requested_from', 'requested_by',
                        'details', 'share_objectives', 'sent', 'replied'),
           'log': ('content')}


class Entry(db.DynamicDocument):

    entry_type = db.StringField(required=True)

    # this is apparently how to do custom validation in mongoengine
    # if someone tries to save entry with fields not in schemas map of tuples
    # above or with unknown entry_type we'll get an validation error
    def clean(self):
        try:
            valid_fields = schemas[self.entry_type]
        except KeyError:
            msg = 'There is no schema defined for %s' % self.entry_type
            raise ValidationError(msg)
        for dynamic_field in self._dynamic_fields.keys():
            if dynamic_field not in valid_fields:
                msg = '%s is not a valid field' % dynamic_field
                raise ValidationError(msg)


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
        Objectives.objects(id=self.id).update_one(
            pull__objectives__id=objective.id)
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
    grade = db.StringField()
    profession = db.StringField()
    # only one objectives set (current year for the moment)
    # change this one current and list of past ones?
    objectives = db.ReferenceField(Objectives)
    other_email = db.ListField(default=[])
    _inbox_email = db.StringField()

    @property
    def inbox_email(self):
        if not self._inbox_email:
            user_name = self.email.split('@')[0]
            inbox_email = "%s@mylog.civilservice.digital" % user_name
            self.inbox_email = inbox_email
        return self._inbox_email

    @inbox_email.setter
    def inbox_email(self, email):
        self._inbox_email = email
        self.save()


class Tag(db.Document):
    owner = db.ReferenceField(User)
    name = db.StringField()


class LogEntry(db.Document):
    created_date = db.DateTimeField(default=datetime.datetime.utcnow)
    content = db.StringField()
    owner = db.ReferenceField(User)
    entry_from = db.StringField()
    tags = db.ListField(db.ReferenceField(Tag), default=[])
    editable = db.BooleanField(default=True)
    link = db.StringField()

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


class FeedbackRequest(db.Document):
    requested_by = db.ReferenceField(User)
    requested_from = db.ReferenceField(User)
    share_objectives = db.BooleanField(default=False)
    sent = db.BooleanField(default=False)
    replied = db.BooleanField(default=False)
    feedback_template = db.StringField()
    log_entry = db.ReferenceField(LogEntry)
