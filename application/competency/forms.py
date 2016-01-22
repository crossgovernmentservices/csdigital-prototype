from flask.ext.login import current_user
from flask.ext.wtf import Form
from wtforms.fields import SelectField, SelectMultipleField
from wtforms.widgets import CheckboxInput, ListWidget


class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


class BehaviourForm(Form):
    behaviours = MultiCheckboxField()


def behaviours_form(behaviours):
    form = BehaviourForm()
    form.behaviours.choices = [
        (behaviour.id, behaviour.effective)
        for behaviour in behaviours]
    return form


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
