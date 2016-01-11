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


class LinkForm(Form):
    objectives = SelectField()


def make_link_form(objectives):
    form = LinkForm()
    form.objectives.choices = [
        (str(objective.id), objective.entry.what)
        for objective in objectives]
    return form
