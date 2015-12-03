from flask.ext.wtf import Form
from wtforms.validators import Required
from wtforms.fields import TextAreaField


class ObjectiveForm(Form):
    what = TextAreaField('What is your objective?', validators=[Required()])
    how = TextAreaField('How will you achieve this?', validators=[Required()])
