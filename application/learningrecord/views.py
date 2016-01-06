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
    current_app,
    request
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

learningrecord = Blueprint('learningrecord', __name__, template_folder='templates')

@learningrecord.route('/learning_record', methods=['POST'])
def add_learning_record():
    record = request.json
    user_email = record['email']
    link = record['link']

    current_app.logger.info(record)

    try:
        entry = Entry()
        entry.link = link
        entry.save()

        user = User.objects.filter(email=user_email).get()
        log_entry = LogEntry(owner=user)

        log_entry.entry_type = 'learning_record'
        log_entry.entry = entry
        log_entry.save()
        log_entry.add_tag('Learning record')

    except DoesNotExist:
        # log and raise so we get sentry notification
        current_app.logger.error('No email: '+ user_email)
        raise

    return 'OK', 200


@learningrecord.route('/learning_record/<id>')
@login_required
def view_learning_record(id):
    log_entry = LogEntry.objects(id=id)
    if not log_entry:
        abort(404)
    log_entry = log_entry.get()

    return redirect(log_entry.entry.link)
