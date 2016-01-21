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
from application.models import LogEntry, User
from application.notes.forms import NoteForm


notes = Blueprint('notes', __name__, template_folder='templates')


def get_note_or_404(id):
    try:
        return LogEntry.objects.get(id=id, entry_type='log')

    except LogEntry.DoesNotExist:
        abort(404)


@notes.route('/notes/<id>/link', methods=['POST'])
def link(id):
    note = get_note_or_404(id)
    form = make_link_form()

    if form.is_submitted():
        if 'competencies' in request.form:
            competency = Competency.objects.get(
                id=request.form['competencies'])
            note.link(competency)
            flash('Competency successfully linked to note')

        elif 'objectives' in request.form:
            objective = LogEntry.objects.get(
                id=request.form['objectives'],
                entry_type='objective')
            note.link(objective)
            flash('Objective successfully linked to note')

    return redirect(url_for('.view', id=id))


@notes.route('/notes/<id>/unlink/<link_id>', methods=['GET', 'POST'])
@login_required
def unlink(id, link_id):
    note = get_note_or_404(id)

    if note.unlink(link_id):
        flash('Removed link')

    else:
        flash('Failed to remove link', 'error')

    return redirect(url_for('.view', id=id))


@notes.route('/notes/add', methods=['GET', 'POST'])
@notes.route('/notes/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id=None):

    note = None
    link_form = None
    if id:
        note = get_note_or_404(id)
        link_form = make_link_form(competencies=True)

    form = NoteForm()

    if form.validate_on_submit():

        if note:
            form.update(note)
            flash('Updated note')

        else:
            note = form.create()
            flash('Added note')

        return redirect(url_for('.view', id=note.id))

    if note:
        form.content.data = note.entry.content
        form.tags.data = ','.join(tag.name for tag in note.tags)

    return render_template(
        'notes/edit.html',
        form=form,
        link_form=link_form,
        note=note)


@notes.route('/notes')
@notes.route('/notes/<id>')
@login_required
def view(id=None):
    note = None

    if id:
        note = get_note_or_404(id)

    return render_template('notes/view.html', note=note)


@notes.route('/notes/<id>/link_to_staff_member', methods=['POST'])
@login_required
def link_staff(id):
    note = get_note_or_404(id)

    try:
        member = User.objects.get(id=request.form['user_id'])

    except User.DoesNotExist:
        abort(404)

    note.link(member)
    return redirect(url_for('.view', id=id))
