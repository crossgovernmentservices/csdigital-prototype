from flask import (
    Blueprint,
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
from application.models import Link, LogEntry
from application.profile.views import update_details_form


competency = Blueprint('competency', __name__, template_folder='templates')


@competency.app_context_processor
def competencies():
    return dict(competencies=Competency.objects)


@competency.route('/competency/<competency_id>/link', methods=['POST'])
@login_required
def link(competency_id):
    competency = Competency.objects.get(id=competency_id)
    objectives = LogEntry.objects.filter(
        owner=current_user._get_current_object(),
        entry_type='objective')

    form = make_link_form(objectives)
    del form.competencies

    if form.validate_on_submit():
        objective = objectives.get(id=form.objectives.data)
        objective.link(competency)
        flash('Competency linked to selected objective')

    return redirect(url_for('.view', competency_id=competency_id))


@competency.route('/competency', methods=['GET', 'POST'])
@competency.route('/competency/<competency_id>', methods=['GET', 'POST'])
@competency.route('/competency/<competency_id>/<level_id>', methods=['GET', 'POST'])
@login_required
def view(competency_id=None, level_id=None):
    competency = None
    if competency_id:
        competency = Competency.objects.get(id=competency_id)

    level = None
    if level_id:
        level = Level.objects.get(id=level_id)

    user = current_user._get_current_object()
    objectives = LogEntry.objects.filter(
        owner=user,
        entry_type='objective')
    link_form = make_link_form(objectives)

    links = Link.objects.filter(owner=user, documents=competency)
    links = [
        doc
        for linked in links
        for doc in linked.documents
        if doc != competency]

    behaviours = []

    if not current_user.grade:
        form = update_details_form()

        if form.validate_on_submit():
            current_user.grade = form.grade.data
            current_user.save()
            flash('Successfully updated profile')
            return redirect(url_for(
                '.view',
                competency_id=competency_id))

        return render_template(
            'competency/view-competency.html',
            competency=competency,
            level=level,
            link_form=link_form,
            links=links,
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
        links=links,
        level=level,
        prev_level=prev_level,
        next_level=next_level,
        competency=competency)
