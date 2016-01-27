from flask import (
    Blueprint,
    flash,
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


@competency.route('/competency/<id>/link', methods=['POST'])
@login_required
def link(id):
    competency = get_or_404(Competency, id=id)
    form = make_link_form(objectives=True, notes=True)

    if form.validate_on_submit():
        objective = LogEntry.objects.get(
            id=request.form['objectives'],
            entry_type='objective')
        objective.link(competency)
        flash('Competency linked to selected objective')

    return redirect(url_for('.view', id=id))


@competency.route('/competency/<id>/unlink/<link_id>', methods=['GET', 'POST'])
@login_required
def unlink(id, link_id):
    competency = get_or_404(Competency, id=id)

    if competency.unlink(link_id):
        flash('Removed link')

    else:
        flash('Failed to remove link', 'error')

    return redirect(url_for('.view', id=id))


@competency.route('/competency', methods=['GET', 'POST'])
def view_all():
    return render_template('competency/view_all.html')


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

    return render_template(
        'competency/view.html',
        level=level,
        competency=get_or_404(Competency, id=id))
