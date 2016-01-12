import datetime

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash
)

from flask.ext.security import login_required
from flask.ext.login import current_user

from application.competency.forms import make_link_form
from application.competency.models import Competency
from application.objectives.forms import ObjectiveForm
from application.utils import a_year_from_now
from application.models import (
    Entry,
    Link,
    LogEntry
)

objectives = Blueprint('objectives', __name__, template_folder='templates')


@objectives.route('/objective')
@login_required
def view_objectives():
    user = current_user._get_current_object()
    objectives = LogEntry.objects.filter(owner=user,
                                         entry_type='objective').all()
    return render_template('objectives/objective-view.html', objectives=objectives)


@objectives.route('/performance-review')
@login_required
def write_performance_review():
    return render_template('objectives/performance-review.html')


@objectives.route('/competency-checker')
@login_required
def check_competency_framework():
    return render_template('objectives/competency-checker.html')


@objectives.route("/objective/add", methods=['GET', 'POST'])
@login_required
def add_objective():

    user = current_user._get_current_object()
    objectives = LogEntry.objects.filter(owner=user,
                                       entry_type='objective').all()
    form = ObjectiveForm()
    if form.validate_on_submit():
        user = current_user._get_current_object()
        entry = Entry()
        entry.how = form.how.data
        entry.what = form.what.data
        entry.started_on = datetime.datetime.utcnow()
        entry.due_by = a_year_from_now()
        entry.save()

        log_entry = LogEntry()
        log_entry.entry_type = 'objective'
        log_entry.owner = user
        log_entry.entry = entry
        log_entry.save()
        log_entry.add_tag('Objective')
        flash('Added objective')
        return redirect(url_for('objectives.view_objective', id=log_entry.id))
    else:
        add_url = url_for('objectives.add_objective')
        return render_template('objectives/add-edit-objective.html',
                               form=form,
                               link_form=None,
                               url=add_url,
                               objectives=objectives)


@objectives.route('/objective/<id>/link', methods=['POST'])
@login_required
def link(id):
    objective = LogEntry.objects.get(id=id, entry_type='objective')
    form = make_link_form(competencies=True)
    del form.objectives

    if form.validate_on_submit():
        competency = Competency.objects.get(id=form.competencies.data)
        objective.link(competency)
        flash('Competency successfully linked to objective')

    else:
        flash('Linking to competency failed', 'error')
        return "%s %s" % (form.errors, form.data)

    return redirect(url_for('.edit_objective', id=id))

@objectives.route("/objective/<id>")
@login_required
def view_objective(id):
  user = current_user._get_current_object()
  objectives = LogEntry.objects.filter(owner=user,
                                       entry_type='objective').all()

  objective = LogEntry.objects.get(id=id, entry_type='objective')

  link_form = make_link_form(competencies=True)
  link_url = url_for('.link', id=id)

  links = Link.objects.filter(documents=objective)
  links = [
      doc
      for link in links
      for doc in link.documents
      if doc != objective]

  return render_template('objectives/objective-view.html',
                        objective=objective,
                        links=links,
                        link_form=link_form,
                        link_url=link_url,
                        objectives=objectives)

@objectives.route("/objective/<id>/edit", methods=['GET', 'POST'])
@login_required
def edit_objective(id):

    objective = LogEntry.objects.get(id=id, entry_type='objective')

    link_form = make_link_form(competencies=True)
    link_url = url_for('.link', id=id)

    links = Link.objects.filter(documents=objective)
    links = [
        doc
        for link in links
        for doc in link.documents
        if doc != objective]

    form = ObjectiveForm()
    if form.validate_on_submit():
        objective.entry.update(what=form.what.data, how=form.how.data)
        objective.entry.save()
        return redirect(url_for('objectives.view_objective', id=id))
    else:
        edit_url = url_for('objectives.edit_objective', id=id)
        form.what.data = objective.entry.what
        form.how.data = objective.entry.how
        return render_template('objectives/add-edit-objective.html',
                               form=form,
                               url=edit_url,
                               link_form=link_form,
                               link_url=link_url,
                               links=links,
                               edit=True)
