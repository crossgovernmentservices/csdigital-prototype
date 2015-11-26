from flask.ext.wtf import Form
from flask.ext.wtf.html5 import EmailField

from wtforms.validators import Required
from wtforms.fields import TextAreaField


class LoginForm(Form):
    email = EmailField('Email address', validators=[Required()])


class EmailForm(Form):
    email = EmailField('Email address', validators=[Required()])


class ObjectiveForm(Form):
    what = TextAreaField('What is your objective?', validators=[Required()])
    how = TextAreaField('How will you achieve this?', validators=[Required()])
