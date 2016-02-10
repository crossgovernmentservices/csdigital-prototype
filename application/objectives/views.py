from flask import (
    Blueprint,
    abort,
    flash,
    jsonify,
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
from application.utils import get_or_404


objectives = Blueprint('objectives', __name__, template_folder='templates')


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
    link = None
    _type = None
    target = None

    if 'competencies' in request.form:
        _type = 'Competency'
        target = get_or_404(Competency, id=request.form['competencies'])

    elif 'notes' in request.form:
        _type = 'Note'
        target = get_or_404(current_user.notes, id=request.form['notes'])

    if target:
        link = objective.link(target)

        if request.is_xhr:
            return jsonify({
                'link': {'id': str(link.id)},
                'target': target,
                'type': _type})

        flash('{} successfully linked to objective'.format(_type))

    else:
        flash('Linking failed', 'error')

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
    if id:
        objective = get_objective_or_404(id=id)

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
        if 'progress' in objective.entry:
            form.progress.data = objective.entry.progress

    return render_template(
        'objectives/edit.html',
        form=form,
        objective=objective)


@objectives.route('/objective/<id>')
@login_required
def view(id):
    return render_template(
        'objectives/view.html',
        objective=get_objective_or_404(id=id),
        evidence_form=EvidenceForm())


@objectives.route('/objective')
@login_required
def view_all():
    return render_template('objectives/view_all.html')


@objectives.route('/objective/staff/<user_id>/<id>')
@login_required
def view_for_user(user_id, id):
    user = get_or_404(User, id=user_id)

    if user not in current_user.staff:
        abort(403)

    objective = get_objective_or_404(id=id)

    return render_template(
        'objectives/view.html',
        objective=objective,
        user=user)


@objectives.route('/objective/staff/<user_id>')
@login_required
def view_all_for_user(user_id):
    user = get_or_404(User, id=user_id)

    if user not in current_user.staff:
        abort(403)

    return render_template('objectives/view_all.html', user=user)


@objectives.route('/objective/staff/<user_id>/<id>/comment', methods=['POST'])
@login_required
def comment(user_id, id):
    user = get_or_404(User, id=user_id)

    if user not in current_user.staff:
        abort(403)

    objective = get_objective_or_404(id=id)

    objective.add_comment(request.form['content'])

    return redirect(url_for('.view_for_user', user_id=user_id, id=id))


@objectives.route('/objective/<id>/evidence/add', methods=['GET', 'POST'])
@login_required
def add_evidence(id):
    objective = get_objective_or_404(id=id)
    form = EvidenceForm()

    if form.validate_on_submit():
        evidence = create_log_entry('evidence', **request.form)
        objective.link(evidence)

        flash('Evidence added')

        return redirect(url_for('.view', id=id))

    return render_template(
        'objectives/add_evidence.html',
        form=form,
        objective=objective)


@objectives.route('/objective/<id>/evidence/note/<note_id>', methods=['GET', 'POST'])
@login_required
def promote_note(id, note_id):
    note = get_or_404(LogEntry, entry_type='log', id=note_id)

    evidence = create_log_entry(
        'evidence',
        title=note.entry.title,
        content=note.entry.content)

    objective = get_objective_or_404(id=id)
    objective.link(evidence)

    flash('Evidence created from note')

    return redirect(url_for('.view', id=id))


@objectives.route('/objective/<id>/evidence/remove/<evidence_id>')
@login_required
def remove_evidence(id, evidence_id):
    objective = get_objective_or_404(id=id)
    evidence = get_or_404(LogEntry, entry_type='evidence', id=evidence_id)
    objective.unlink(evidence)
    evidence.delete()
    flash('Evidence removed')
    return redirect(url_for('.view', id=id))
