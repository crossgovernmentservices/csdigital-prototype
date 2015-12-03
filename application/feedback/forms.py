from flask.ext.wtf import Form

from wtforms.validators import Required
from wtforms.fields import TextAreaField


class FeedbackForm(Form):
    feedback = TextAreaField('Your feedback', validators=[Required()])
