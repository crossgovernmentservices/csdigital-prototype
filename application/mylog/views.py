import hashlib
import hmac

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
    Entry,
    LogEntry,
    Tag
)
from application.competency.models import Competency
from application.mylog.forms import LogEntryForm


mylog = Blueprint('mylog', __name__, template_folder='templates')


def get_logentry_or_404(id):
    try:
        return LogEntry.objects.get(id=id)

    except LogEntry.DoesNotExist:
        abort(404)


@mylog.route('/my-log')
@login_required
def view_mylog():
    owner = current_user._get_current_object()
    filtered = False
    tags = Tag.objects.filter(owner=owner)

    if request.args.get('tag'):
        tag = tags.get(name__iexact=request.args.get('tag'))
        log_entries = LogEntry.objects.filter(
            owner=owner,
            tags__in=[tag])
        filtered = True

    else:
        log_entries = LogEntry.objects.filter(owner=owner)

    tags = Tag.objects.filter(owner=owner)
    return render_template('mylog/log.html',
                           log_entries=log_entries,
                           tags=tags,
                           filtered=filtered)


@mylog.route('/my-log/entry', methods=['GET', 'POST'])
@login_required
def add_log_entry():
    form = LogEntryForm()

    if form.validate_on_submit():
        entry = Entry.objects.create(
            content=form.content.data)

        log_entry = LogEntry.objects.create(
            entry_type='log',
            owner=current_user._get_current_object(),
            entry=entry)

        for tag in form.tags.data.split(','):
            log_entry.add_tag(tag)

        flash('Entry saved')

        return redirect(url_for('mylog.view_mylog'))

    return render_template(
        'mylog/add-entry.html',
        form=form,
        competencies=Competency.objects)


@mylog.route('/my-log/entry/<id>', methods=['GET', 'POST'])
@login_required
def view_log_entry(id):
    entry = get_logentry_or_404(id)

    if request.method == 'POST':
        entry.entry.update(content=request.form['content'])

        for tag in request.form['tags'].split(','):
            entry.add_tag(tag)

        flash('entry updated')

    return render_template('mylog/entry.html', entry=entry)


@mylog.route('/my-log/entry/<id>/tags.json', methods=['GET', 'POST'])
@login_required
def tag_entry(id):
    entry = get_logentry_or_404(id)

    if request.method == 'POST':
        entry.add_tag(request.json.get('tag'))

    return jsonify({'tags': [tag.name for tag in entry.tags]})


@mylog.route('/my-log/tags.json')
@login_required
def find_tags():
    tag_name = request.args.get('tag-name')
    owner = current_user._get_current_object()

    if tag_name:
        tags = Tag.objects.filter(
            name__istartswith=tag_name,
            owner=owner)

    else:
        tags = Tag.objects.filter(owner=owner)

    return jsonify({'tags': tags})


@mylog.route('/my-log/inbox', methods=['POST'])
def inbox():
    if verified(request):
        LogEntry.create_from_email(request)
        return 'OK', 200

    return 'Not acceptable', 406


def verified(req):
    signature = req.form.get('signature')
    key = current_app.config['MAILGUN_API_KEY'].encode('utf-8')
    msg = '{timestamp}{token}'.format(**req.form).encode('utf-8')

    return signature == hmac.new(
        key=key,
        msg=msg,
        digestmod=hashlib.sha256).hexdigest()
