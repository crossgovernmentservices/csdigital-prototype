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
        links = Link.objects.filter(owner=user, documents=self)
        return [
            doc
            for link in links
            for doc in link.documents
            if doc != self]

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


class Behaviour(db.Document):
    effective = db.StringField()
    ineffective = db.StringField()
    level = db.ReferenceField(Level)
    competency = db.ReferenceField(Competency)
    behaviour_id = db.IntField()
