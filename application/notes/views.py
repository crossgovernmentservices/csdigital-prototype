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
from application.models import Entry, LogEntry
from application.notes.forms import NoteForm


notes = Blueprint('notes', __name__, template_folder='templates')


def get_note_or_404(id):
    try:
        return LogEntry.objects.get(id=id, entry_type='log')

    except LogEntry.DoesNotExist:
        abort(404)


@notes.route('/notes/create', methods=['GET', 'POST'])
def create():
    form = NoteForm()

    if form.validate_on_submit():
        user = current_user._get_current_object()
        entry = Entry(content=form.content.data)
        entry.save()

        note = LogEntry(entry_type='log', owner=user)
        note.entry = entry
        note.save()

        if form.tags.data:
            for tag in form.tags.data.split(','):
                note.add_tag(tag.strip())

        flash('Note saved')
        return redirect(url_for('.view'))

    return render_template('notes/edit.html', form=form)


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


@notes.route('/notes/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    note = get_note_or_404(id)
    form = NoteForm()
    form.init_from_note(note)

    if form.validate_on_submit():
        note.entry.content = form.content.data
        for tag in form.tags.data.split(','):
            note.add_tag(tag.strip())
        note.save()
        flash('Note updated')
        return redirect(url_for('.view', id=id))

    return render_template('notes/edit.html', form=form, note=note)


@notes.route('/notes')
@notes.route('/notes/<id>')
@login_required
def view(id=None):
    note = None

    if id:
        note = get_note_or_404(id)

    return render_template('notes/view.html', note=note)
