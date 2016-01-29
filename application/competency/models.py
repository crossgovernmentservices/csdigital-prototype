from flask.ext.mongoengine import MongoEngine

from application.models import Linkable


db = MongoEngine()


class Level(db.Document):
    description = db.StringField()
    level_id = db.IntField()

    @property
    def prev(self):
        if '_prev' not in self and self.level_id > 1:
            self._prev = Level.objects.get(level_id=self.level_id - 1)
        return self._prev

    @property
    def next(self):
        if '_next' not in self and self.level_id < 6:
            self._next = Level.objects.get(level_id=self.level_id + 1)
        return self._next


class CompetencyCluster(db.Document):
    name = db.StringField(required=True)
    goal = db.StringField()
    cluster_id = db.IntField()


class Competency(db.Document, Linkable):
    name = db.StringField(required=True)
    overview = db.StringField()
    cluster = db.ReferenceField(CompetencyCluster)
    competency_id = db.IntField()

    def behaviours(self, level):
        return Behaviour.objects.filter(level=level, competency=self)


class Behaviour(db.Document):
    effective = db.StringField()
    ineffective = db.StringField()
    level = db.ReferenceField(Level)
    competency = db.ReferenceField(Competency)
    behaviour_id = db.IntField()
