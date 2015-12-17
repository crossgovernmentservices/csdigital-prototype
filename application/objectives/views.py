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

from application.objectives.forms import ObjectiveForm
from application.utils import a_year_from_now
from application.models import (
    Entry,
    LogEntry
)

objectives = Blueprint('objectives', __name__, template_folder='templates')


@objectives.route('/objectives')
@login_required
def view_objectives():
    user = current_user._get_current_object()
    objectives = LogEntry.objects.filter(owner=user,
                                          entry_type='objective').all()
    return render_template('objectives/objectives.html', objectives=objectives)


@objectives.route('/performance-review')
@login_required
def write_performance_review():
    return render_template('objectives/performance-review.html')


@objectives.route('/competency-checker')
@login_required
def check_competency_framework():
    return render_template('objectives/competency-checker.html')


@objectives.route("/objectives/add", methods=['GET', 'POST'])
@login_required
def add_objective():
    form = ObjectiveForm()
    if form.validate_on_submit():
        entry = Entry()
        entry.entry_type = 'objective'
        entry.how = form.how.data
        entry.what = form.what.data
        entry.started_on = datetime.datetime.utcnow()
        entry.due_by = a_year_from_now()
        entry.save()

        log_entry = LogEntry()
        log_entry.owner = user
        log_entry.entry = entry
        log_entry.save()
        log_entry.add_tag('Objective')
        flash('Added objective')
        return redirect(url_for('objectives.view_objectives'))
    else:
        add_url = url_for('objectives.add_objective')
        return render_template('objectives/add-edit-objective.html',
                               form=form,
                               url=add_url)


@objectives.route("/objectives/<id>", methods=['GET', 'POST'])
@login_required
def edit_objective(id):
    form = ObjectiveForm()
    if form.validate_on_submit():
        objective = Objective.objects(id=id).update(what=form.what.data,
                                                    how=form.how.data)
        return redirect(url_for('objectives.view_objectives'))
    else:
        edit_url = url_for('objectives.edit_objective', id=id)
        objective = Objective.objects(id=id).get()
        form.what.data = objective.what
        form.how.data = objective.how
        return render_template('objectives/add-edit-objective.html',
                               form=form,
                               url=edit_url,
                               edit=True)
