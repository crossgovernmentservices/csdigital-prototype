import datetime

from flask.ext.security import (
    UserMixin,
    RoleMixin
)

from flask.ext.mongoengine import MongoEngine

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
    status = db.StringField(default='In progress') # ? something else I think
    objectives = db.ListField(db.ReferenceField(Objective), default=[])

    def add(self, objective):
        self.objectives.append(objective)
        self.save()

    def remove(self, objective):
        Objectives.objects(id=self.id).update_one(pull__objectives__id=objective.id)
        self.save()


class FeedbackRequest(db.EmbeddedDocument):
    recipient_email = db.StringField(max_length=255)
    status = db.StringField(default='Requested')  # How do I do mongo enums?


class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)


class User(db.Document, UserMixin):
    email = db.StringField(max_length=255)
    password = db.StringField(max_length=255)
    active = db.BooleanField(default=True)
    confirmed_at = db.DateTimeField()
    roles = db.ListField(db.ReferenceField(Role), default=[])
    full_name = db.StringField()
    objectives = db.ReferenceField(Objectives)
    feedback_requests = db.ListField(db.EmbeddedDocumentField(FeedbackRequest), default=[])
    # only one set (current year for the moment)
    # change this one current and list of past ones?
    other_email = db.ListField(default=[])

    def add_request_if_not_present(self, feedback_request):
        for feedback in self.feedback_requests:
            if feedback.recipient_email == feedback_request.recipient_email:
                return
        else:
            self.feedback_requests.append(feedback_request)

