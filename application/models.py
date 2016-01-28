import datetime

from flask import current_app
from flask.ext.security import (
    UserMixin,
    RoleMixin
)
from flask.ext.login import current_user
from flask.ext.mongoengine import MongoEngine
from mongoengine.queryset import queryset_manager
from mongoengine.errors import ValidationError


db = MongoEngine()


class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)


class User(db.Document, UserMixin):
    email = db.StringField(required=True)
    password = db.StringField()
    active = db.BooleanField(default=True)
    confirmed_at = db.DateTimeField()
    roles = db.ListField(db.ReferenceField(Role), default=[])
    full_name = db.StringField()
    grade = db.StringField()
    profession = db.StringField()
    other_email = db.ListField(default=[])
    inbox_email = db.StringField()
    staff = db.ListField(db.ReferenceField('User'), default=[])
    manager = db.ReferenceField('User')

    @property
    def objectives(self):
        return LogEntry.objects.filter(owner=self, entry_type='objective')

    @property
    def notes(self):
        return LogEntry.objects.filter(owner=self, entry_type='log').order_by(
            '-created_date')

    @property
    def feedback(self):
        return LogEntry.objects.filter(owner=self, entry_type='feedback')

    @property
    def tags(self):
        return Tag.objects.filter(owner=self)

    @property
    def competencies(self):
        # TODO
        from application.competency.models import Competency
        return Competency.objects

    @property
    def manager_notes(self):
        links = Link.objects.filter(documents=self)
        return [
            doc
            for link in links
            for doc in link.documents
            if doc != self]

    @property
    def is_manager(self):
        return bool(self.staff)

    def remove_staff(self, user):
        if user in self.staff:
            self.update(pull__staff=user)
            user.update(manager=None)

    def add_staff(self, user):
        if user not in self.staff and not user.manager:
            self.update(add_to_set__staff=user)
            user.update(manager=self)


def make_inbox_email(email):
    return '{user}@{domain}'.format(
        user=email.split('@')[0],
        domain=current_app.config['EMAIL_DOMAIN'])


class Link(db.Document):
    """
    Link between documents, eg: Objective<->Competency
    """
    documents = db.ListField(db.GenericReferenceField(), default=[])
    owner = db.ReferenceField(User)


class Tag(db.Document):
    owner = db.ReferenceField(User)
    name = db.StringField()


schemas = {
    'objective': ('how', 'what', 'started_on', 'due_by', 'title', 'progress'),
    'feedback': (
        'template',
        'requested_from',
        'requested_by',
        'requested_from_name',
        'requested_by_name',
        'details',
        'share_objectives',
        'objectives',
        'sent',
        'replied'),
    'comment': ('content',),
    'evidence': ('content', 'title'),
    'log': ('content', 'title')
}


class Entry(db.DynamicDocument):

    def __unicode__(self):
        data = ''
        if 'title' in self:
            data = self.title
        elif 'details' in self:
            data = self.details
        return data


class LogEntry(db.Document):
    created_date = db.DateTimeField(default=datetime.datetime.utcnow)
    owner = db.ReferenceField(User)
    entry_from = db.StringField()
    tags = db.ListField(db.ReferenceField(Tag), default=[])
    editable = db.BooleanField(default=True)
    entry_type = db.StringField(required=True)
    entry = db.ReferenceField(Entry, required=True)

    def add_tag(self, name):
        name = name.strip()

        if name:

            try:
                tag = Tag.objects.get(name__iexact=name, owner=self.owner)

            except Tag.DoesNotExist:
                tag = Tag.objects.create(name=name, owner=self.owner)

            self.update(add_to_set__tags=tag)

    def has_tag(self, name):
        name = name.strip().lower()

        try:
            tag = Tag.objects.get(name__iexact=name, owner=self.owner)

        except Tag.DoesNotExist:
            return False

        return tag in self.tags

    @queryset_manager
    def objects(doc_cls, queryset):
        return queryset.order_by('-created_date')

    # this is apparently how to do custom validation in mongoengine
    # if someone tries to save entry with fields not in schemas map of tuples
    # above or with unknown entry_type we'll get an validation error
    def clean(self):
        try:
            valid_fields = schemas[self.entry_type]
        except KeyError:
            msg = 'There is no schema defined for %s' % self.entry_type
            raise ValidationError(msg)
        for dynamic_field in self.entry._dynamic_fields.keys():
            if dynamic_field not in valid_fields:
                msg = '%s is not a valid field' % dynamic_field
                raise ValidationError(msg)

    def has_link(self, other):
        links = Link.objects.filter(documents=self).filter(documents=other)
        return links.count() != 0

    def link(self, other):
        if self != other and not self.has_link(other):
            link = Link(documents=[self, other])
            link.owner = self.owner
            link.save()

    def unlink(self, other_id):
        links = Link.objects.filter(
            documents=self,
            owner=current_user._get_current_object())

        for link in links:
            doc_a, doc_b = link.documents

            # XXX link_id is a GUID, but not unique across collections
            if doc_a == self and str(doc_b.id) == other_id:
                link.delete()
                return True

            if doc_b == self and str(doc_a.id) == other_id:
                link.delete()
                return True

        return False

    @property
    def links(self):
        links = Link.objects.filter(documents=self)
        return [
            doc
            for link in links
            for doc in link.documents
            if doc != self]

    @property
    def comments(self):
        return [
            link for link in self.links
            if 'entry_type' in link and link.entry_type == 'comment']

    @property
    def evidence(self):
        return [
            link for link in self.links
            if 'entry_type' in link and link.entry_type == 'evidence']

    def add_comment(self, content):
        comment = create_log_entry('comment', content=content)
        self.link(comment)

    @classmethod
    def create_from_email(cls, request):
        email = {
            'sender': request.form['sender'],
            'recipient': request.form['recipient'],
            'subject': request.form.get('subject', ''),
            'body': request.form.get(
                'stripped-text',  # try body without signature first
                request.form.get('body-plain', ''))}

        current_app.logger.debug('Received email: {}'.format(email))

        try:
            user = User.objects.get(inbox_email=email['recipient'])

        except User.DoesNotExist:
            current_app.logger.error(
                'No user found with inbox_email="{recipient}"'.format(**email))
            raise

        note = create_log_entry(
            'log',
            title=email['subject'].strip(),
            content=email['body'],
            entry_from=email['sender'],
            owner=user)

        note.add_tag('Email')

        return note

    def __unicode__(self):
        return 'type={0.entry_type}, entry={0.entry}'.format(self)


def create_log_entry(_type, **kwargs):
    data = {}
    _kwargs = dict(kwargs)
    for key, val in _kwargs.items():
        if key in schemas[_type]:
            data[key] = kwargs.pop(key)

    entry = Entry.objects.create(**data)

    owner = kwargs.pop('owner', current_user._get_current_object())

    return LogEntry.objects.create(
        entry_type=_type,
        entry=entry,
        owner=owner,
        **kwargs)
