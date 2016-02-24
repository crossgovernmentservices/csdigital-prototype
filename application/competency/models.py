import mongoengine as db

from application.models import Linkable


class Level(db.Document):
    description = db.StringField()
    level_id = db.IntField()

    @property
    def prev(self):
        if self.level_id > 1:
            return Level.objects.get(level_id=self.level_id - 1)

    @property
    def next(self):
        if self.level_id < 6:
            return Level.objects.get(level_id=self.level_id + 1)


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

    def objectives(self, user):
        return [
            objective
            for objective in self.linked
            if objective.entry_type == 'objective' and objective.owner == user]

    def to_json(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'overview': self.overview,
            'cluster': self.cluster.name}


class Behaviour(db.Document):
    effective = db.StringField()
    ineffective = db.StringField()
    level = db.ReferenceField(Level)
    competency = db.ReferenceField(Competency)
    behaviour_id = db.IntField()
