from flask.ext.wtf import Form
from wtforms.validators import Required
from wtforms.fields import (
    TextAreaField,
    StringField
)


class LogEntryForm(Form):
    tags = StringField('tags')
    content = TextAreaField('Content', validators=[Required()])
