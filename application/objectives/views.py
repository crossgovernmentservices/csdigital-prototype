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

from application.competency.models import Competency
from application.models import (
    Link,
    LogEntry,
    User,
    create_log_entry,
    entry_from_json)
from application.objectives.forms import EvidenceForm, ObjectiveForm
from application.utils import get_or_404


objectives = Blueprint('objectives', __name__, template_folder='templates')


def get_objective_or_404(**kwargs):
    return get_or_404(LogEntry, entry_type='objective', **kwargs)


@objectives.route('/performance-review')
@login_required
def write_performance_review():
    return render_template('objectives/performance-review.html')


def get_link_target(data):
    _type = None
    target = None

    if 'competencies' in data:
        _type = 'Competency'
        target = get_or_404(Competency, id=data['competencies'])

    elif 'notes' in data:
        _type = 'Note'
        target = get_or_404(current_user.notes, id=data['notes'])

    return _type, target


@objectives.route('/objective/<id>/links.json', methods=['GET', 'POST'])
@login_required
def links(id):
    objective = get_objective_or_404(id=id)

    if request.method == 'POST':
        _, target = get_link_target(request.get_json())

        if target:
            objective.link(target)
            objective.reload()

        else:
            return jsonify({'error': 'Linking failed'})

    return jsonify({'linked': [l.to_json() for l in objective.linked]})


@objectives.route('/objective/<id>/links/<link_id>', methods=['GET', 'DELETE'])
@login_required
def link(id, link_id):
    objective = get_objective_or_404(id)
    get_or_404(Link, id=link_id)

    if request.method == 'DELETE':
        objective.remove_link(link_id)
        return jsonify({})

    return jsonify({})


@objectives.route('/objective/<id>/link', methods=['POST'])
@login_required
def make_link(id):
    objective = get_objective_or_404(id=id)
    _type, target = get_link_target(request.form)

    if target:
        objective.link(target)
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


@objectives.route('/objective/<id>.json', methods=['GET', 'PATCH', 'PUT'])
@login_required
def objective_json(id):
    objective = get_objective_or_404(id=id)

    if request.method in ['PATCH', 'PUT']:
        objective.entry.update(**entry_from_json('objective', request.json))
        objective.add_tags(request.json.get('tags', []))
        objective.reload()

    return jsonify(objective.to_json())


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


@objectives.route('/objective/<id>/comments.json', methods=['GET', 'POST'])
@login_required
def comments(id):
    objective = get_objective_or_404(id=id)

    if request.method == 'POST':

        if objective.owner not in current_user.staff:
            abort(403)

        objective.add_comment(request.get_json()['content'])
        objective.reload()

    return jsonify({'comments': [c.to_json() for c in objective.comments]})


@objectives.route('/objective/staff/<user_id>/<id>/comment', methods=['POST'])
@login_required
def comment(user_id, id):
    user = get_or_404(User, id=user_id)

    if user not in current_user.staff:
        abort(403)

    objective = get_objective_or_404(id=id)

    objective.add_comment(request.form['content'])

    return redirect(url_for('.view_for_user', user_id=user_id, id=id))


@objectives.route('/objective/<id>/evidence.json', methods=['GET', 'POST'])
@login_required
def evidence(id):
    objective = get_objective_or_404(id=id)

    if request.method == 'POST':
        create_log_entry('evidence', **request.get_json())
        objective.link(evidence)
        objective.reload()

    return jsonify({'evidence': [e.to_json() for e in objective.evidence]})


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
