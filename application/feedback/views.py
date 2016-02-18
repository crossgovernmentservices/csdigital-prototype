from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for
)
from flask.ext.login import current_user
from flask.ext.mail import Message
from flask.ext.security import login_required

from application.extensions import mail
from application.feedback.forms import FeedbackForm
from application.models import (
    User,
    LogEntry,
    create_log_entry
)
from application.utils import get_or_404


feedback = Blueprint('feedback', __name__, template_folder='templates')


@feedback.route('/get-feedback', methods=['GET', 'POST'])
@login_required
def get_feedback():

    if request.method == 'POST':
        recipients = User.objects.filter(
            email__in=request.form.getlist('q'))
        share = bool(request.form.get('share-objectives'))
        user = current_user._get_current_object()

        if recipients:
            for recipient in recipients:

                feedback = create_log_entry(
                    'feedback',
                    requested_by=user.email,
                    requested_from=recipient.email,
                    requested_by_name=user.full_name,
                    requested_from_name=recipient.full_name,
                    template=request.form.get('feedback-template'),
                    share_objectives=share)

                if share:
                    for objective in user.objectives:
                        feedback.link(objective)

                feedback.add_tag('Feedback')

                _send_feedback_email(feedback, user, recipient)

            flash('Submitted request')

            return redirect(url_for('.requested_feedback'))

        flash('Failed submitting request(s)', 'error')

    return render_template('feedback/get-feedback.html')


@feedback.route('/give-feedback')
@login_required
def give_feedback():
    user = current_user._get_current_object()
    feedback = user.feedback

    return render_template(
        'feedback/feedback-for-others.html',
        feedback_requests=feedback)


@feedback.route('/give-feedback/<id>', methods=['GET', 'POST'])
@login_required
def reply_to_feedback(id):
    form = FeedbackForm()
    feedback_request = get_or_404(LogEntry, id=id)

    if form.validate_on_submit():
        feedback_request.entry.update(
            replied=True,
            details=form.feedback.data)
        flash("Saved feedback")

        return redirect(url_for('feedback.give_feedback'))

    return render_template(
        'feedback/give-feedback.html',
        form=form,
        feedback_request=feedback_request)


# your requests for feedback from other people
@feedback.route('/feedback')
@login_required
def requested_feedback():
    user = current_user._get_current_object()

    return render_template(
        'feedback/feedback-for-me.html',
        feedback_requests=user.feedback_requests)


@feedback.route('/feedback/<id>')
@login_required
def view_requested_feedback(id):
    feedback_request = get_or_404(LogEntry, id=id, entry_type='feedback')

    return render_template(
        'feedback/view-feedback.html',
        feedback_request=feedback_request)


def _send_feedback_email(feedback, request_by, request_from):

    msg = Message(
        html=render_template(
            'feedback/email/feedback-request.html',
            sender=request_by,
            recipient=request_from,
            url=url_for('.reply_to_feedback', id=feedback.id, _external=True)),
        subject="Feedback request from {name}".format(
            name=request_by.full_name),
        sender="noreply@civilservice.digital",
        recipients=[feedback.entry.requested_from])

    try:
        mail.send(msg)

    except Exception as e:
        current_app.logger.error("failed to send email", e)
        abort(500)

    feedback.entry.update(sent=True)
