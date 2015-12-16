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
    FeedbackRequest,
    LogEntry
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
            feedback_request = FeedbackRequest(requested_by=user)
            other_user = User.objects.filter(email=recipient).first()
            feedback_request.requested_from = other_user
            feedback_request.share_objectives = share_objectives
            template = request.form.get('feedback-template')
            feedback_request.feedback_template = template
            feedback_request.save()
            _send_feedback_email(feedback_request)
        flash('Submitted request')

    return render_template('feedback/get-feedback.html')


@feedback.route('/give-feedback')
@login_required
def give_feedback():
    user = current_user._get_current_object()
    requests = FeedbackRequest.objects.filter(requested_from=user).all()
    return render_template('feedback/feedback-for-others.html',
                           feedback_requests=requests)


@feedback.route('/give-feedback/<id>', methods=['GET', 'POST'])
@login_required
def reply_to_feedback(id):
    form = FeedbackForm()
    feedback_request = FeedbackRequest.objects(id=id).get()

    if form.validate_on_submit():

        log_entry = LogEntry()
        log_entry.owner = feedback_request.requested_by
        log_entry.content = form.feedback.data
        feedback_url = url_for('feedback.view_requested_feedback',
                               id=feedback_request.id)
        log_entry.link = feedback_url
        log_entry.editable = False
        log_entry.entry_from = current_user.full_name
        log_entry.save()
        log_entry.add_tag('Feedback')

        feedback_request.replied = True
        feedback_request.log_entry = log_entry
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
    feedback_requests = FeedbackRequest.objects(requested_by=user).all()
    return render_template('feedback/feedback-for-me.html',
                           feedback_requests=feedback_requests)


@feedback.route('/feedback/<id>')
@login_required
def view_requested_feedback(id):
    feedback_request = FeedbackRequest.objects(id=id).get()
    return render_template('feedback/view-feedback.html',
                           feedback_request=feedback_request)


def _send_feedback_email(feedback_request):
    host = current_app.config['HOST']
    if 'localhost' in host:
        host = "%s:8000" % host
    url = "http://%s/give-feedback/%s" % (host, feedback_request.id)
    html = render_template('feedback/email/feedback-request.html',
                           request=feedback_request,
                           url=url)
    msg = Message(html=html,
                  subject="Feedback request from test",
                  sender="noreply@csdigital.notrealgov.uk",
                  recipients=[feedback_request.requested_from.email])
    try:
        mail.send(msg)
        feedback_request.sent = True
        feedback_request.save()
    except Exception as ex:
        current_app.logger.error("failed to send email", ex)
        return 'Internal Server Error', 500
