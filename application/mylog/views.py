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
from flask.ext.mongoengine import DoesNotExist

from application.models import (
    Entry,
    LogEntry,
    Tag,
    User
)


from application.mylog.forms import LogEntryForm

mylog = Blueprint('mylog', __name__, template_folder='templates')


@mylog.route('/my-log')
@login_required
def view_mylog():
    owner = current_user._get_current_object()
    filtered = False
    if request.args.get('tag'):
        tag = Tag.objects.filter(name__iexact=request.args.get('tag'),
                                 owner=owner).first()
        log_entries = LogEntry.objects.filter(owner=owner,
                                              tags__in=[tag]).all()
        filtered = True
    else:
        log_entries = LogEntry.objects.filter(owner=owner).all()

    tags = Tag.objects.filter(owner=owner).all()
    return render_template('mylog/log.html',
                           log_entries=log_entries,
                           tags=tags,
                           filtered=filtered)


@mylog.route('/my-log/entry', methods=['GET', 'POST'])
@login_required
def add_log_entry():
    form = LogEntryForm()
    if form.validate_on_submit():
        entry = Entry()
        entry.entry_type = 'log'
        entry.content = form.content.data
        entry.save()

        log_entry = LogEntry()
        log_entry.owner = current_user._get_current_object()
        log_entry.entry = entry
        log_entry.save()

        if form.tags.data:
            tags = form.tags.data.split(',')
            for tag in tags:
                log_entry.add_tag(tag.strip())
        flash('Entry saved')
        return redirect(url_for('mylog.view_mylog'))
    return render_template('mylog/add-entry.html', form=form)


@mylog.route('/my-log/entry/<id>', methods=['GET', 'POST'])
@login_required
def view_log_entry(id):
    entry = LogEntry.objects(id=id)
    if not entry:
        abort(404)
    entry = entry.get()
    if request.method == 'GET':
        return render_template('mylog/entry.html', entry=entry)
    else:
        content = request.form['content']
        tags = request.form['tags']
        if tags:
            tags = tags.split(',')
            for tag in tags:
                entry.add_tag(tag)
        entry.content = content
        entry.save()
        entry = LogEntry.objects(id=id).get()
        flash('entry updated')
        return render_template('mylog/entry.html', entry=entry)


@mylog.route('/my-log/entry/<id>/tags', methods=['GET', 'POST'])
@login_required
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
@login_required
def find_tags():
    tag_name = request.args.get('tag-name')
    owner = current_user._get_current_object()
    if tag_name:
        tags = Tag.objects.filter(name__istartswith=tag_name,
                                  owner=owner).all()
    else:
        tags = Tag.objects.filter(owner=owner).all()
    return jsonify({"tags": tags})


@mylog.route('/my-log/inbox', methods=['POST'])
def inbox():
    if not _verified(request):
        # just ignore and move along
        current_app.logger.info('Unverfied request')
        return 'OK', 200
    else:
        _send_to_mylog(request)
    return 'OK', 200


def _verified(req):
    token = req.form.get('token')
    timestamp = req.form.get('timestamp')
    signature = req.form.get('signature')
    if None in (token, timestamp, signature):
        return False
    key = current_app.config['MAILGUN_API_KEY'].encode('utf-8')
    msg = '{}{}'.format(timestamp, token).encode('utf-8')
    return signature == hmac.new(key=key,
                                 msg=msg,
                                 digestmod=hashlib.sha256).hexdigest()


def _send_to_mylog(req):
    sender = request.form.get('sender')
    recipient = request.form.get('recipient')
    subject = request.form.get('subject', '')
    body = request.form.get('body-plain', '')

    current_app.logger.info('Inbound email')
    current_app.logger.info(sender)
    current_app.logger.info(recipient)
    current_app.logger.info(subject)
    current_app.logger.info(body)
    current_app.logger.info('End inbound email')

    try:
        user = User.objects.filter(_inbox_email=recipient).get()
        log_entry = LogEntry(owner=user)
        log_entry.entry_from = sender
        sender = "From: %s" % sender
        content = '\n'.join([subject, body, sender])
        log_entry.content = content
        log_entry.save()
        log_entry.add_tag('Email')
    except DoesNotExist:
        # log and raise so we get sentry notification
        current_app.logger.error('No inbox email:' + recipient)
        raise
