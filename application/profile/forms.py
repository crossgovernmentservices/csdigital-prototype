from flask.ext.wtf import Form
from flask.ext.wtf.html5 import EmailField
from wtforms.validators import Required
from wtforms.fields import TextField


class EmailForm(Form):
    email = EmailField('Email address', validators=[Required()])

class UpdateDetailsForm(Form):
    grade = TextField('Grade')
    profession = TextField('Profession')