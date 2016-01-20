from flask.ext.wtf import Form
from flask.ext.wtf.html5 import EmailField
from wtforms.validators import Required
from wtforms.fields import (
    SelectField,
    TextField)


class EmailForm(Form):
    email = EmailField('Email address', validators=[Required()])


class UpdateDetailsForm(Form):
    full_name = TextField('Full Name')
    grade = SelectField('Grade')
    profession = TextField('Profession')
