from flask.ext.login import current_user
from flask.ext.wtf import Form
from wtforms.fields import SelectMultipleField

from application.competency.models import Competency


def make_link_form(**kwargs):
    form = kwargs.pop('form', Form)
    user = current_user._get_current_object()

    def choices(items):
        return [(str(item.id), str(item)) for item in items]

    for linktype in ['competencies', 'notes', 'objectives']:
        if kwargs.get(linktype, False):

            if linktype == 'competencies':
                _choices = choices(Competency.objects)
            else:
                _choices = choices(getattr(user, linktype))

            setattr(form, linktype, SelectMultipleField(
                choices=_choices))

    return form()
