import datetime

from flask.ext.login import current_user
from flask.ext.wtf import Form
from wtforms.validators import DataRequired, Required
from wtforms.fields import StringField, TextAreaField

from application.models import Entry, LogEntry
from application.utils import a_year_from_now


class ObjectiveForm(Form):
    title = StringField('Title', validators=[Required()])
    what = TextAreaField('What is your objective?', validators=[Required()])
    how = TextAreaField('How will you achieve this?', validators=[Required()])

    def update(self, objective):
        objective.entry.update(
            title=self.title.data,
            what=self.what.data,
            how=self.how.data)
        objective.entry.save()

    def create(self):
        entry = Entry(
            title=self.title.data,
            what=self.what.data,
            how=self.how.data,
            started_on=datetime.datetime.utcnow(),
            due_by=a_year_from_now())
        entry.save()

        objective = LogEntry(
            entry_type='objective',
            owner=current_user._get_current_object(),
            entry=entry)
        objective.save()

        objective.add_tag('Objective')

        return objective


class EvidenceForm(Form):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content')
