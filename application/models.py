import datetime

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

    @property
    def objectives(self):
        return LogEntry.objects.filter(owner=self, entry_type='objective')

    @property
    def notes(self):
        return LogEntry.objects.filter(owner=self, entry_type='log')

    @property
    def feedback(self):
        return LogEntry.objects.filter(owner=self, entry_type='feedback')

    @property
    def tags(self):
        return Tag.objects.filter(owner=self)


class Link(db.Document):
    """
    Link between documents, eg: Objective<->Competency
    """
    documents = db.ListField(db.GenericReferenceField(), default=[])
    owner = db.ReferenceField(User)


class Tag(db.Document):
    owner = db.ReferenceField(User)
    name = db.StringField()


schemas = {'objective': ('how', 'what', 'started_on', 'due_by', 'title'),
           'feedback': ('template', 'requested_from', 'requested_by',
                        'requested_from_name', 'requested_by_name',
                        'details', 'share_objectives', 'objectives',
                        'sent', 'replied'),
           'log': ('content', 'title')}


class Entry(db.DynamicDocument):
    pass


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
