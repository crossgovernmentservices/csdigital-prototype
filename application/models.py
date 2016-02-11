import datetime
import logging

from flask import current_app
from flask.ext.security import (
    UserMixin,
    RoleMixin
)
from flask.ext.login import current_user
import mongoengine as db
from mongoengine.queryset import queryset_manager
from mongoengine.errors import ValidationError

from application.utils import get_or_404


class Link(db.Document):
    """
    Link between documents, eg: Objective<->Competency
    """
    documents = db.ListField(db.GenericReferenceField(), default=[])
    owner = db.ReferenceField('User')


class Linkable(object):

    @property
    def links(self):
        return Link.objects.filter(documents=self)

    def has_link(self, other):
        return self.links.filter(documents=other).count() != 0

    def link(self, other):
        if self != other and not self.has_link(other):
            return Link.objects.create(documents=[self, other])

    def unlink(self, other):

        if isinstance(other, str):
            unlinked = False
            for linked in self.linked:
                if str(getattr(linked, 'id', '')) == other:
                    self.unlink(linked)
                    unlinked = True
            return unlinked

        return self.links.filter(documents=other).delete()

    def remove_link(self, link_id):
        self.links.filter(id=link_id).delete()

    @property
    def linked(self):
        return [
            doc
            for link in self.links.select_related()
            for doc in link.documents
            if doc != self]


class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)


class User(db.Document, UserMixin, Linkable):
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

    def get_or_404(self, cls, **kwargs):
        return get_or_404(cls, owner=self, **kwargs)

    @property
    def objectives(self):
        return LogEntry.objects.filter(owner=self, entry_type='objective')

    @property
    def last_updated_objective(self):
        objectives = self.objectives
        by_last_updated = sorted(
            objectives,
            key=lambda o: o.entry.last_updated or o.created_date,
            reverse=True)
        if by_last_updated:
            return by_last_updated[0]

    def add_objective(self, **kwargs):
        return create_log_entry('objective', owner=self, **kwargs)

    @property
    def notes(self):
        return LogEntry.objects.filter(owner=self, entry_type='log').order_by(
            '-created_date')

    @property
    def last_updated_note(self):
        notes = self.notes
        by_last_updated = sorted(
            notes,
            key=lambda n: n.entry.last_updated or n.created_date,
            reverse=True)
        if by_last_updated:
            return by_last_updated[0]

    def add_note(self, **kwargs):
        return create_log_entry('log', owner=self, **kwargs)

    @property
    def feedback(self):
        return LogEntry.objects.filter(owner=self, entry_type='feedback')

    @property
    def tags(self):
        return Tag.objects.filter(owner=self)

    @property
    def competencies(self):
        return set([
            competency
            for objective in self.objectives
            for competency in objective.linked
            if competency.__class__.__name__ == 'Competency'])

    @property
    def manager_notes(self):
        # XXX only manager notes are linked to users at the moment
        return self.linked

    @property
    def is_manager(self):
        return bool(self.staff)

    def remove_staff(self, user):
        if user in self.staff:
            self.update(pull__staff=user)
            user.update(manager=None)

    def add_staff(self, user):
        if not user.manager:

            admin_role = Role.objects.get(name='ADMIN')
            if admin_role not in user.roles:
                self.update(add_to_set__staff=user)
                user.update(manager=self)

            else:
                logging.warn("can't add ADMIN {.full_name} as staff".format(
                    user))

        else:
            logging.warn("{.full_name} already has a manager".format(user))

    def to_json(self):
        return {
            'id': str(self.id),
            'full_name': self.full_name,
            'email': self.email,
            'grade': self.grade,
            'profession': self.profession}


def make_inbox_email(email):
    return '{user}@{domain}'.format(
        user=email.split('@')[0],
        domain=current_app.config['EMAIL_DOMAIN'])


class Tag(db.Document):
    owner = db.ReferenceField(User)
    name = db.StringField()


schemas = {
    'objective': (
        'how',
        'what',
        'started_on',
        'due_by',
        'title',
        'progress'),
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
    last_updated = db.DateTimeField(default=None)

    def save(self, *args, **kwargs):
        self.last_updated = datetime.datetime.utcnow()
        return super(Entry, self).save(*args, **kwargs)

    def update(self, *args, **kwargs):
        self.last_updated = datetime.datetime.utcnow()
        return super(Entry, self).update(*args, **kwargs)

    def __unicode__(self):
        data = ''
        if 'title' in self:
            data = self.title
        elif 'details' in self:
            data = self.details
        return data

    def to_json(self):
        return dict(
            id=str(self.id),
            **dict((k, getattr(self, k)) for k in self if k not in ['id']))


class LogEntry(db.Document, Linkable):
    created_date = db.DateTimeField(default=datetime.datetime.utcnow)
    owner = db.ReferenceField(User)
    entry_from = db.StringField()
    tags = db.ListField(db.ReferenceField(Tag), default=[])
    editable = db.BooleanField(default=True)
    entry_type = db.StringField(required=True)
    entry = db.ReferenceField(Entry, required=True)

    def to_json(self):
        return {
            'id': str(self.id),
            'entry_type': self.entry_type,
            'entry': self.entry.to_json(),
            'created_date': self.created_date,
            'tags': [tag.name for tag in self.tags]}

    def add_tag(self, name):
        name = name.strip()

        if name:

            try:
                tag = Tag.objects.get(name__iexact=name, owner=self.owner)

            except Tag.DoesNotExist:
                tag = Tag.objects.create(name=name, owner=self.owner)

            self.update(add_to_set__tags=tag)

    def add_tags(self, tags):
        tags = filter(None, map(lambda s: s.strip(), tags))

        if tags:
            tags = Tag.objects.filter(name__in=tags, owner=self.owner)
            self.update(add_to_set__tags=list(tags))

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

    def _linked_log_entries(self, entry_type):
        return [
            link for link in self.linked
            if 'entry_type' in link and link.entry_type == entry_type]

    @property
    def comments(self):
        return list(reversed(self._linked_log_entries('comment')))

    @property
    def latest_comment(self):
        comments = self.comments
        if comments:
            return comments[0]

    @property
    def notes(self):
        return self._linked_log_entries('log')

    @property
    def evidence(self):
        return list(reversed(self._linked_log_entries('evidence')))

    @property
    def latest_evidence(self):
        evidence = self.evidence
        if evidence:
            return evidence[0]

    @property
    def competencies(self):
        return [
            link for link in self.linked
            if link.__class__.__name__ == 'Competency']

    @property
    def linked_staff(self):
        return [
            link for link in self.linked
            if link.__class__.__name__ == 'User']

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

    data = {}
    _kwargs = dict(kwargs)
    for key, val in _kwargs.items():
        if key in ['owner', 'entry_from', 'tags']:
            data[key] = kwargs.pop(key)

    owner = kwargs.pop('owner', current_user._get_current_object())

    return LogEntry.objects.create(
        entry_type=_type,
        entry=entry,
        owner=owner,
        **data)


def entry_from_json(entry_type, json):
    schema = schemas[entry_type]
    return {k: json[k] for k in schema if k in json}
