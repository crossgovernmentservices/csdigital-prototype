from flask import (
    Blueprint,
    render_template,
    current_app,
    flash,
    request
)

from flask.ext.security import login_required
from flask.ext.login import current_user

from flask.ext.mail import Message

from application.extensions import mail
from application.frontend.forms import FeedbackForm
from application.models import (
    User,
    FeedbackRequest
)

feedback = Blueprint('feedback', __name__, template_folder='templates')


@feedback.route('/get-feedback', methods=['GET', 'POST'])
@login_required
def get_feedback():
    if request.method == 'POST':
        recipients = request.form.getlist('email')
        share_objectives = request.form.get('share-objectives')
        for recipient in recipients:
            feedback_request = FeedbackRequest(requested_by=current_user._get_current_object())
            other_user = User.objects.filter(email=recipient).first()
            feedback_request.requested_from = other_user
            if share_objectives:
                feedback_request.share_objectives = True
            feedback_request.save()
            _send_feedback_email(feedback_request)
            flash('Submitted request')

    return render_template('feedback/get-feedback.html')


@feedback.route('/give-feedback/<id>', methods=['GET', 'POST'])
@login_required
def give_feedback(id):
    form = FeedbackForm()
    feedback_request = FeedbackRequest.objects(id=id).get()
    objectives = None
    if feedback_request.share_objectives:
        objectives = feedback_request.requested_by.objectives
    if form.validate_on_submit():
        feedback_request.feedback_details = form.feedback.data
        feedback_request.save()
        flash("Saved feedback")
        return render_template('feedback/give-feedback.html', form=form, feedback_request=feedback_request, objectives=objectives, saved=True)
    else:
        return render_template('feedback/give-feedback.html', form=form, feedback_request=feedback_request, objectives=objectives)


# your requests for feedback from other people
@feedback.route('/feedback')
@login_required
def requested_feedback(id=None):
    feedback_requests = FeedbackRequest.objects(requested_by=current_user._get_current_object()).all()
    return render_template('feedback/requested-feedback.html', feedback_requests=feedback_requests)


@feedback.route('/feedback/<id>')
@login_required
def view_requested_feedback(id):
    feedback_request = FeedbackRequest.objects(id=id).get()
    return render_template('feedback/view-feedback.html', feedback_request=feedback_request)


def _send_feedback_email(feedback_request):
    host = current_app.config['HOST']
    if 'localhost' in host:
        host = "%s:8000" % host
    url = "http://%s/give-feedback/%s" % (host, feedback_request.id)
    html = render_template('feedback/email/feedback-request.html', request=feedback_request, url=url)
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
