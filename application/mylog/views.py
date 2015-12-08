from flask import (
    Blueprint,
    render_template,
    flash,
    redirect,
    url_for,
    abort,
    jsonify,
    request,
    current_app
)

from flask.ext.security import login_required
from flask.ext.login import current_user

from application.models import (
    LogEntry,
    Tag
)

from application.mylog.forms import LogEntryForm

mylog = Blueprint('mylog', __name__, template_folder='templates')


@mylog.route('/my-log')
@login_required
def view_mylog():
    owner = current_user._get_current_object()
    filtered = False
    if request.args.get('tag'):
        tag = Tag.objects.filter(name__iexact=request.args.get('tag'), owner=owner).first()
        log_entries = LogEntry.objects.filter(owner=owner, tags__in=[tag]).all()
        filtered = True
    else:
        log_entries = LogEntry.objects.filter(owner=owner).all()

    tags = Tag.objects.filter(owner=owner).all()
    return render_template('mylog/log.html', log_entries=log_entries, tags=tags, filtered=filtered)


@mylog.route('/my-log/entry', methods=['GET', 'POST'])
def add_log_entry():
    form = LogEntryForm()
    if form.validate_on_submit():
        entry = LogEntry(content=form.content.data)
        entry.owner = current_user._get_current_object()
        entry.save()
        flash('Entry saved')
        return redirect(url_for('mylog.view_mylog'))
    return render_template('mylog/add-entry.html', form=form)


@mylog.route('/my-log/entry/<id>')
def view_log_entry(id):
    entry = LogEntry.objects(id=id)
    if not entry:
        abort(404)
    return render_template('mylog/entry.html', entry=entry.get())


@mylog.route('/my-log/entry/<id>/tags', methods=['GET',' POST'])
def tag_entry(id):
    entry = LogEntry.objects(id=id).get()
    if not entry:
        abort(404)
    if request.method == 'GET':
        tags = [tag.name for tag in entry.tags]
        return jsonify({"tags": tags})
    else:
        tag_name = request.json.get('tag')
        entry.add_tag(tag_name)
        entry.save()
        return 'OK', 200


@mylog.route('/my-log/tags.json')
def find_tags():
    tag_name = request.args.get('tag-name')
    if tag_name:
        tags = Tag.objects.filter(name__istartswith=tag_name).all()
    else:
        tags = Tag.objects.all()
    return jsonify({"tags": tags})
