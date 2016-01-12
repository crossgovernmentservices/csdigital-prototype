from flask.ext.login import current_user
from flask.ext.mongoengine import MongoEngine

from application.models import Link


db = MongoEngine()


class Level(db.Document):
    description = db.StringField()
    level_id = db.IntField()


class CompetencyCluster(db.Document):
    name = db.StringField(required=True)
    goal = db.StringField()
    cluster_id = db.IntField()


class Competency(db.Document):
    name = db.StringField(required=True)
    overview = db.StringField()
    cluster = db.ReferenceField(CompetencyCluster)
    competency_id = db.IntField()

    @property
    def links(self):
        user = current_user._get_current_object()
        return Link.objects.filter(owner=user, documents=self)


class Behaviour(db.Document):
    effective = db.StringField()
    ineffective = db.StringField()
    level = db.ReferenceField(Level)
    competency = db.ReferenceField(Competency)
    behaviour_id = db.IntField()
