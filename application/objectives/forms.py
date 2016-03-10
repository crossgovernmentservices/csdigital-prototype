import datetime

from flask.ext.wtf import Form
from wtforms.validators import DataRequired, Required
from wtforms.fields import StringField, TextAreaField

from application.models import create_log_entry
from application.utils import a_year_from_now


class ObjectiveForm(Form):
    title = StringField('Title', validators=[Required()])
    what = TextAreaField('What is your objective?', validators=[Required()])
    how = TextAreaField('How will you achieve this?', validators=[Required()])
    measures = TextAreaField('Measurements')
    outcomes = TextAreaField('Outcomes (optional)')
    deliverables = TextAreaField('Deliverables (optional)')
    progress = TextAreaField('What progress have you made? (optional - for project work only)')

    def update(self, objective):
        objective.entry.update(
            title=self.title.data,
            what=self.what.data,
            measures=self.measures.data,
            outcomes=self.outcomes.data,
            deliverables=self.deliverables.data,
            progress=self.progress.data,
            how=self.how.data)

    def create(self):
        objective = create_log_entry(
            'objective',
            title=self.title.data,
            what=self.what.data,
            how=self.how.data,
            measures=self.measures.data,
            outcomes=self.outcomes.data,
            deliverables=self.deliverables.data,
            progress=self.progress.data,
            started_on=datetime.datetime.utcnow(),
            due_by=a_year_from_now())

        objective.add_tag('Objective')

        return objective


class EvidenceForm(Form):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content')
