from flask.ext.login import current_user
from flask.ext.wtf import Form
from wtforms.fields import SelectField


def make_link_form(**enable):
    form = Form()
    user = current_user._get_current_object()

    def choices(items):
        return [(str(item.id), str(item)) for item in items]

    for linktype in ['competencies', 'notes', 'objectives']:
        if enable.get(linktype, False):
            setattr(form, linktype, SelectField(
                choices=choices(getattr(user, linktype))))

    return form
