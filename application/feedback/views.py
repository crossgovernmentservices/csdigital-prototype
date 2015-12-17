from flask import (
    Blueprint,
    render_template,
    current_app,
    flash,
    request,
    url_for,
    redirect
)

from flask.ext.security import login_required
from flask.ext.login import current_user

from flask.ext.mail import Message

from application.extensions import mail
from application.feedback.forms import FeedbackForm

from application.models import (
    User,
    LogEntry,
    Entry
)

feedback = Blueprint('feedback', __name__, template_folder='templates')


@feedback.route('/get-feedback', methods=['GET', 'POST'])
@login_required
def get_feedback():
    if request.method == 'POST':
        recipients = request.form.getlist('email')
        share = request.form.get('share-objectives')
        share_objectives = share == 'share-objectives'

        for recipient in recipients:
            user = current_user._get_current_object()
            other_user = User.objects.filter(email=recipient).first()

            entry = Entry()
            entry.entry_type = 'feedback'
            entry.requested_by = user.email
            entry.requested_from = other_user.email
            entry.template = request.form.get('feedback-template')
            entry.share_objectives = share_objectives
            if share_objectives:
                # get and attach objectives
                pass
            entry.save()

            log_entry = LogEntry()
            log_entry.owner = user
            log_entry.entry = entry
            log_entry.save()
            log_entry.add_tag('Feedback')

            _send_feedback_email(log_entry, user, other_user)
        flash('Submitted request')

    return render_template('feedback/get-feedback.html')


@feedback.route('/give-feedback')
@login_required
def give_feedback():
    user = current_user._get_current_object()
    requests = Entry.objects.filter(entry_type='feedback',
                                    requested_from=user.email).all()
    return render_template('feedback/feedback-for-others.html',
                           feedback_requests=requests)


@feedback.route('/give-feedback/<id>', methods=['GET', 'POST'])
@login_required
def reply_to_feedback(id):
    form = FeedbackForm()
    feedback_request = Entry.objects(id=id).get()

    if form.validate_on_submit():
        feedback_request.replied = True
        feedback_request.details = form.feedback.data
        feedback_request.save()
        flash("Saved feedback")

        return redirect(url_for('feedback.give_feedback'))
    else:
        return render_template('feedback/give-feedback.html',
                               form=form,
                               feedback_request=feedback_request)


# your requests for feedback from other people
@feedback.route('/feedback')
@login_required
def requested_feedback():
    user = current_user._get_current_object()
    feedback_requests = Entry.objects.filter(entry_type='feedback',
                                             requested_by=user.email).all()

    return render_template('feedback/feedback-for-me.html',
                           feedback_requests=feedback_requests)


@feedback.route('/feedback/<id>')
@login_required
def view_requested_feedback(id):
    feedback_request = Entry.objects(id=id).get()
    return render_template('feedback/view-feedback.html',
                           feedback_request=feedback_request)


def _send_feedback_email(feedback, request_by, request_from):
    host = current_app.config['HOST']
    if 'localhost' in host:
        host = "%s:8000" % host
    url = "http://%s/give-feedback/%s" % (host, feedback.id)
    html = render_template('feedback/email/feedback-request.html',
                           request_by=request_by,
                           request_from=request_from,
                           url=url)
    msg = Message(html=html,
                  subject="Feedback request from test",
                  sender="noreply@csdigital.notrealgov.uk",
                  recipients=[feedback.entry.requested_from])
    try:
        mail.send(msg)
        feedback.entry.sent = True
        feedback.entry.save()
        feedback.save()
    except Exception as ex:
        current_app.logger.error("failed to send email", ex)
        return 'Internal Server Error', 500
