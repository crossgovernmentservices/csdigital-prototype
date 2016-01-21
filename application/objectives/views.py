from flask import (
    Blueprint,
    abort,
    render_template,
    redirect,
    url_for,
    flash
)
from flask.ext.login import current_user
from flask.ext.security import login_required

from application.competency.forms import make_link_form
from application.competency.models import Competency
from application.objectives.forms import ObjectiveForm
from application.models import LogEntry, User


objectives = Blueprint('objectives', __name__, template_folder='templates')


def get_objective_or_404(id):
    try:
        return LogEntry.objects.get(id=id, entry_type='objective')

    except LogEntry.DoesNotExist:
        abort(404)


@objectives.route('/performance-review')
@login_required
def write_performance_review():
    return render_template('objectives/performance-review.html')


@objectives.route('/objective/<id>/link', methods=['POST'])
@login_required
def link(id):
    objective = get_objective_or_404(id)
    form = make_link_form(competencies=True)
    del form.objectives

    if form.validate_on_submit():
        competency = Competency.objects.get(id=form.competencies.data)
        objective.link(competency)
        flash('Competency successfully linked to objective')

    else:
        flash('Linking to competency failed', 'error')

    return redirect(url_for('.view', id=id))


@objectives.route('/objective/<id>/unlink/<link_id>', methods=['GET', 'POST'])
@login_required
def unlink(id, link_id):
    objective = get_objective_or_404(id)

    if objective.unlink(link_id):
        flash('Removed link')

    else:
        flash('Failed to remove link', 'error')

    return redirect(url_for('.view', id=id))


@objectives.route('/objective/add', methods=['GET', 'POST'])
@objectives.route("/objective/<id>/edit", methods=['GET', 'POST'])
@login_required
def edit(id=None):

    objective = None
    link_form = None
    if id:
        objective = get_objective_or_404(id)
        link_form = make_link_form(competencies=True)

    form = ObjectiveForm()

    if form.validate_on_submit():

        if objective:
            form.update(objective)
            flash('Updated objective')

        else:
            objective = form.create()
            flash('Added objective')

        return redirect(url_for('.view', id=objective.id))

    if objective:
        form.what.data = objective.entry.what
        form.how.data = objective.entry.how

    return render_template(
        'objectives/edit.html',
        form=form,
        link_form=link_form,
        objective=objective)


@objectives.route('/objective')
@objectives.route('/objective/<id>')
@login_required
def view(id=None):
    objective = None
    if id:
        objective = get_objective_or_404(id)

    link_form = make_link_form(competencies=True)

    return render_template(
        'objectives/view.html',
        objective=objective,
        link_form=link_form)


@objectives.route('/objective/staff/<user_id>')
@objectives.route('/objective/staff/<user_id>/<id>')
@login_required
def view_others(user_id, id=None):
    try:
        user = User.objects.get(id=user_id)

    except User.DoesNotExist:
        abort(404)

    if user not in current_user.staff:
        abort(403)

    objective = None
    if id:
        objective = get_objective_or_404(id)

    return render_template(
        'objectives/view.html',
        objective=objective,
        user=user,
        link_form=None)
