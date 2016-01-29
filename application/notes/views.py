from flask import (
    Blueprint,
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
from application.models import LogEntry, Tag, User
from application.notes.forms import NoteForm
from application.utils import get_or_404


notes = Blueprint('notes', __name__, template_folder='templates')


@notes.route('/notes/<id>/link', methods=['POST'])
@login_required
def link(id):
    note = get_or_404(LogEntry, entry_type='log', id=id)
    form = make_link_form(competencies=True, objectives=True)

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
    note = get_or_404(LogEntry, entry_type='log', id=id)

    note.remove_link(link_id)

    flash('Removed link')

    return redirect(url_for('.view', id=id))


@notes.route('/notes/add', methods=['GET', 'POST'])
@notes.route('/notes/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id=None):

    note = None
    link_form = None
    if id:
        note = get_or_404(LogEntry, entry_type='log', id=id)
        link_form = make_link_form(competencies=True, objectives=True)

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
@login_required
def view_all():
    return render_template('notes/view_all.html')


@notes.route('/notes/<id>')
@login_required
def view(id):
    note = get_or_404(LogEntry, entry_type='log', id=id)

    return render_template('notes/view.html', note=note)


@notes.route('/notes/<id>.json')
@login_required
def view_json(id):
    note = get_or_404(LogEntry, entry_type='log', id=id)
    return jsonify({
        'created_date': note.created_date,
        'last_updated': note.entry.last_updated,
        'title': note.entry.title,
        'content': note.entry.content,
        'tags': [tag.name for tag in note.tags]})


@notes.route('/notes/tag/<tag>')
@login_required
def by_tag(tag):
    tag = current_user.get_or_404(Tag, name__iexact=tag)

    notes = current_user.notes.filter(tags__in=[tag])

    return render_template('notes/by-tag.html', tag=tag, notes=notes)


@notes.route('/notes/<id>/link_to_staff_member', methods=['POST'])
@login_required
def link_staff(id):
    note = get_or_404(LogEntry, entry_type='log', id=id)

    member = get_or_404(User, id=request.form['user_id'])

    note.link(member)
    return redirect(url_for('.view', id=id))
