from flask.ext.wtf import Form
from wtforms.validators import Required
from wtforms.fields import TextAreaField


class LogEntryForm(Form):
    content = TextAreaField('Content', validators=[Required()])
