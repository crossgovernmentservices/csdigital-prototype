from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    url_for)
from flask.ext.login import current_user
from flask.ext.security import login_required

from application.competency.forms import behaviours_form, make_link_form
from application.competency.models import (
    Behaviour,
    Competency,
    Level)
from application.models import LogEntry
from application.profile.views import update_details_form


competency = Blueprint('competency', __name__, template_folder='templates')


@competency.app_context_processor
def competencies():
    return dict(competencies=Competency.objects)


def get_competency_or_404(id):
    try:
        return Competency.objects.get(id=id)

    except Competency.DoesNotExist:
        abort(404)


@competency.route('/competency/<id>/link', methods=['POST'])
@login_required
def link(id):
    competency = get_competency_or_404(id)
    objectives = LogEntry.objects.filter(
        owner=current_user._get_current_object(),
        entry_type='objective')

    form = make_link_form(objectives)
    del form.competencies

    if form.validate_on_submit():
        objective = objectives.get(id=form.objectives.data)
        objective.link(competency)
        flash('Competency linked to selected objective')

    return redirect(url_for('.view', id=id))


@competency.route('/competency/<id>/unlink/<link_id>', methods=['GET', 'POST'])
@login_required
def unlink(id, link_id):
    competency = get_competency_or_404(id)

    if competency.unlink(link_id):
        flash('Removed link')

    else:
        flash('Failed to remove link', 'error')

    return redirect(url_for('.view', id=id))


@competency.route('/competency', methods=['GET', 'POST'])
@competency.route('/competency/<id>', methods=['GET', 'POST'])
@competency.route('/competency/<id>/<level_id>', methods=['GET', 'POST'])
@login_required
def view(id=None, level_id=None):
    competency = None
    if id:
        competency = Competency.objects.get(id=id)

    level = None
    if level_id:
        level = Level.objects.get(id=level_id)

    user = current_user._get_current_object()
    objectives = LogEntry.objects.filter(
        owner=user,
        entry_type='objective')
    link_form = make_link_form(objectives)

    behaviours = []

    if not current_user.grade:
        form = update_details_form()

        if form.validate_on_submit():
            current_user.grade = form.grade.data
            current_user.save()
            flash('Successfully updated profile')
            return redirect(url_for('.view', id=id))

        return render_template(
            'competency/view-competency.html',
            competency=competency,
            level=level,
            link_form=link_form,
            form=form)

    if not level:
        level = Level.objects.get(description=current_user.grade)

    prev_level = None
    if level.level_id > 1:
        prev_level = Level.objects.get(level_id=level.level_id - 1)

    next_level = None
    if level.level_id < 6:
        next_level = Level.objects.get(level_id=level.level_id + 1)

    form = None
    if competency:
        behaviours = Behaviour.objects.filter(
            level=level,
            competency=competency)
        form = behaviours_form(behaviours)

    return render_template(
        'competency/view-competency.html',
        behaviours=behaviours,
        form=form,
        link_form=link_form,
        level=level,
        prev_level=prev_level,
        next_level=next_level,
        competency=competency)
