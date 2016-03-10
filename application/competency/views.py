from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    request,
    render_template,
    url_for)
from flask.ext.login import current_user
from flask.ext.security import login_required

from application.competency.forms import make_link_form
from application.competency.models import (
    Competency,
    Level)
from application.models import LogEntry
from application.profile.views import update_details_form
from application.utils import get_or_404


competency = Blueprint('competency', __name__, template_folder='templates')


@competency.app_context_processor
def competencies():
    return dict(competencies=Competency.objects)


@competency.context_processor
def grade_form():
    return dict(grade_form=update_details_form())


def get_link_target(data):
    _type = None
    target = None

    if 'objectives' in data:
        _type = 'Objective'
        target = get_or_404(current_user.objectives, id=data['objectives'])

    elif 'notes' in data:
        _type = 'Note'
        target = get_or_404(current_user.notes, id=data['notes'])

    return _type, target


@competency.route('/competency/<id>/link', methods=['POST'])
@login_required
def link(id):
    competency = get_or_404(Competency, id=id)
    _type, target = get_link_target(request.form)

    if target:
        competency.link(target)
        flash('{} successfully linked to competency'.format(_type))

    else:
        flash('Linking failed', 'error')

    return redirect(url_for('.view', id=id))


@competency.route('/competency/<id>/unlink/<other_id>', methods=['GET', 'POST'])
@login_required
def unlink(id, other_id):
    competency = get_or_404(Competency, id=id)
    other = get_or_404(LogEntry, id=other_id)

    if competency.unlink(other):
        flash('Removed link')

    else:
        flash('Failed to remove link', 'error')

    return redirect(url_for('.view', id=id))


@competency.route('/competency', methods=['GET', 'POST'])
@login_required
def view_all():
    not_linked = Competency.objects.filter(
        id__nin=[c.id for c in current_user.competencies])
    return render_template(
        'competency/view_all.html',
        comps_not_linked=not_linked)


@competency.route('/competency/<id>/level/<level_id>.json')
@login_required
def competency_json(id, level_id):
    level = get_or_404(Level, id=level_id)
    competency = get_or_404(Competency, id=id)
    return jsonify({
        'competency': competency,
        'level': level,
        'behaviours': competency.behaviours(level),
        'next_level': level.next,
        'prev_level': level.prev})


@competency.route('/competency/<id>', methods=['GET', 'POST'])
@competency.route('/competency/<id>/<level_id>', methods=['GET', 'POST'])
@login_required
def view(id=None, level_id=None):
    level = None

    if level_id:
        level = get_or_404(Level, id=level_id)

    elif current_user.grade:
        level = Level.objects.get(description=current_user.grade)

    if not current_user.grade:
        form = update_details_form()

        if form.validate_on_submit():
            current_user.update(grade=form.grade.data)
            flash('Successfully updated profile')
            return redirect(url_for('.view', id=id))

    not_linked = Competency.objects.filter(
        id__nin=[c.id for c in current_user.competencies])

    return render_template(
        'competency/view.html',
        level=level,
        competency=get_or_404(Competency, id=id),
        comps_not_linked=not_linked)
