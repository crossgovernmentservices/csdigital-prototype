import re

from flask import (
    Blueprint,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for)
from flask.ext.login import current_user
from flask.ext.security import login_required
from mongoengine import Q

from application.competency.forms import make_link_form
from application.competency.models import Competency
from application.models import LogEntry, Tag, User, entry_from_json
from application.notes.forms import NoteForm
from application.utils import get_or_404


notes = Blueprint('notes', __name__, template_folder='templates')


def _link(note, data):
    linked = False

    for competency_id in data.get('competencies', []):
        competency = Competency.objects.get(id=competency_id)
        note.link(competency)
        linked = True

    for objective_id in data.get('objectives', []):
        objective = LogEntry.objects.get(
            id=objective_id,
            entry_type='objective')
        note.link(objective)
        linked = True

    return linked


def remove_broken_links(note, links):
    existing = note.linked
    to_remove = [l for l in existing if str(l.id) not in links]
    query = Q(id__in=[])

    for linked in to_remove:
        query = query | Q(documents=linked)

    note.links.filter(query).delete()


@notes.route('/notes/<id>/link', methods=['POST'])
@login_required
def link(id):
    queue_links = False

    if id == 'add':
        queue_links = True

    else:
        note = get_or_404(LogEntry, entry_type='log', id=id)

    form = make_link_form(competencies=True, objectives=True)

    if form.is_submitted():

        if queue_links:
            links = session.get('links', {})
            for key, values in list(request.form.lists()):
                links[key] = values
            session['links'] = links

        elif _link(note, dict(request.form.lists())):
            flash('Link successful')

    return redirect(url_for('.view', id=id))


@notes.route('/notes/<id>/unlink/<link_id>', methods=['GET', 'POST'])
@login_required
def unlink(id, link_id):
    note = get_or_404(LogEntry, entry_type='log', id=id)

    note.unlink(link_id)

    flash('Removed link')

    return redirect(url_for('.view', id=id))


@notes.route('/notes/add', methods=['GET', 'POST'])
@notes.route('/notes/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id=None):

    note = None
    if id:
        note = get_or_404(LogEntry, entry_type='log', id=id)

    form = make_link_form(form=NoteForm, competencies=True, objectives=True)

    if form.validate_on_submit():

        if note:
            form.update(note)
            flash('Updated note')

        else:
            note = form.create()
            flash('Added note')

        remove_broken_links(note, form.competencies.data)
        remove_broken_links(note, form.objectives.data)
        _link(note, dict(request.form.lists()))

        return redirect(url_for('.view', id=note.id))

    if note:
        form.content.data = note.entry.content
        form.tags.data = ','.join(tag.name for tag in note.tags)

    return render_template(
        'notes/edit.html',
        form=form,
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


@notes.route('/notes/<id>.json', methods=['GET', 'PATCH', 'PUT'])
@login_required
def view_json(id):
    note = get_or_404(LogEntry, entry_type='log', id=id)

    if request.method in ['PATCH', 'PUT']:
        note.entry.update(**entry_from_json('log', request.json))
        note.add_tags(request.json.get('tags', []))
        note.reload()

    return jsonify(note.to_json())


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


@notes.route('/notes/search.json')
@login_required
def search():
    search_term = request.args.get('q')
    notes = []

    if search_term:
        notes = current_user.notes

        def match_query(note):
            return (
                re.search(search_term, note.entry.content, re.I) or
                re.search(search_term, note.entry.title, re.I))

        notes = filter(match_query, notes)

    return jsonify({'results': [
        {'name': n.entry.title, 'value': str(n.id)} for n in notes]})
