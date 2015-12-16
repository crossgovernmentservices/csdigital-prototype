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

from application.models import Objective

objectives = Blueprint('objectives', __name__, template_folder='templates')


@objectives.route('/objectives')
@login_required
def view_objectives():
    return render_template('objectives/objectives.html')


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
        flash('Added objective')
        objective = Objective(what=form.what.data, how=form.how.data)
        objective.save()
        current_user.objectives.add(objective)
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
