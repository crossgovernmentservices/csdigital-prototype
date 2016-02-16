import datetime

import mongoengine as db


class Audit(db.Document):
    owner = db.ReferenceField('User')
    created_date = db.DateTimeField(default=datetime.datetime.utcnow)
    commercial = db.IntField()
    digital = db.IntField()
    delivery = db.IntField()
    leadership = db.IntField()
