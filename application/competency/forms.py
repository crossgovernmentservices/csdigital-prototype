from flask.ext.wtf import Form
from wtforms.fields import SelectField, SelectMultipleField
from wtforms.widgets import CheckboxInput, ListWidget

from application.competency.models import Competency


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
    competencies = SelectField(choices=[])
    objectives = SelectField(choices=[])


def make_link_form(objectives=[], competencies=False):
    form = LinkForm()

    if competencies:
        form.competencies.choices = [
            (str(competency.id), competency.name)
            for competency in Competency.objects]

    if objectives:
        form.objectives.choices = [
            (str(objective.id), objective.entry.what)
            for objective in objectives]
    return form
