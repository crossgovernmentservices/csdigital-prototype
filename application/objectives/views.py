from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for)
from flask.ext.login import current_user
from flask.ext.security import login_required

from application.competency.forms import make_link_form
from application.competency.models import Competency
from application.models import LogEntry, User, create_log_entry
from application.objectives.forms import EvidenceForm, ObjectiveForm


objectives = Blueprint('objectives', __name__, template_folder='templates')


def get_or_404(cls, **kwargs):
    try:
        return cls.objects.get(**kwargs)

    except cls.DoesNotExist:
        abort(404)


def get_objective_or_404(**kwargs):
    return get_or_404(LogEntry, entry_type='objective', **kwargs)


@objectives.route('/performance-review')
@login_required
def write_performance_review():
    return render_template('objectives/performance-review.html')


@objectives.route('/objective/<id>/link', methods=['POST'])
@login_required
def link(id):
    objective = get_objective_or_404(id=id)
    form = make_link_form(competencies=True, notes=True)
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
    objective = get_objective_or_404(id=id)

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
        objective = get_objective_or_404(id=id)
        link_form = make_link_form(competencies=True, notes=True)

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
        objective = get_objective_or_404(id=id)

    link_form = make_link_form(competencies=True, notes=True)

    return render_template(
        'objectives/view.html',
        objective=objective,
        link_form=link_form)


@objectives.route('/objective/staff/<user_id>')
@objectives.route('/objective/staff/<user_id>/<id>')
@login_required
def view_others(user_id, id=None):
    user = get_or_404(User, id=user_id)

    if user not in current_user.staff:
        abort(403)

    objective = None
    if id:
        objective = get_objective_or_404(id=id)

    return render_template(
        'objectives/view.html',
        objective=objective,
        user=user,
        link_form=None)


@objectives.route('/objective/staff/<user_id>/<id>/comment', methods=['POST'])
@login_required
def comment(user_id, id):
    user = get_or_404(User, id=user_id)

    if user not in current_user.staff:
        abort(403)

    objective = get_objective_or_404(id=id)

    objective.add_comment(request.form['content'])

    return redirect(url_for('.view_others', user_id=user_id, id=id))


@objectives.route('/objective/<id>/evidence/add', methods=['GET', 'POST'])
@login_required
def add_evidence(id):
    objective = get_objective_or_404(id=id)
    form = EvidenceForm()

    if form.validate_on_submit():
        evidence = create_log_entry(
            'evidence',
            title=form.title.data,
            content=form.content.data)

        objective.link(evidence)

        flash('Evidence added')

        return redirect(url_for('.view', id=id))

    return render_template(
        'objectives/add_evidence.html',
        form=form,
        objective=objective)
