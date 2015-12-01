from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    current_app,
    flash,
    request,
    jsonify,
    json
)

from flask.ext.security import login_required
from flask.ext.security.utils import login_user
from flask.ext.login import current_user

from flask.ext.mail import Message
from application.extensions import mail

from application.frontend.forms import (
    LoginForm,
    EmailForm,
    ObjectiveForm,
    FeedbackForm
)

from application.models import (
    User,
    Objectives,
    FeedbackRequest,
    Objective
)

frontend = Blueprint('frontend', __name__, template_folder='templates')


@frontend.route('/', methods=['GET', 'POST'])
def index():
    from application.extensions import user_datastore
    if current_user and current_user.is_authenticated():
        return redirect('/profile')
    form = LoginForm()
    if form.validate_on_submit():
        email = form.data['email'].strip()
        user = user_datastore.get_user(email)
        if not user:
            flash("You don't have a user account yet")
            return redirect(url_for('.index'))
        logged_in = login_user(user)
        if logged_in:
            return redirect('/profile')
    else:
        return render_template('index.html', form=form)


@frontend.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


@frontend.route('/performance-review')
@login_required
def performance_review():
    return render_template('performance-review.html')


@frontend.route('/users.json')
@login_required
def users():
    q = request.args['q']
    users = User.objects.only('email').filter(email__icontains=q)
    return jsonify({'users': users})


@frontend.route("/performance-review/add-objective", methods=['GET', 'POST'])
@login_required
def add_objective():
    form = ObjectiveForm()
    if form.validate_on_submit():
        message = 'Added objective'
        flash(message)
        objective = Objective(what=form.what.data, how=form.how.data)
        objective.save()
        current_user.objectives.add(objective)
        return redirect(url_for('frontend.performance_review'))
    else:
        add_url = '/performance-review/add-objective'
        return render_template('add-objective.html', form=form, url=add_url)


@frontend.route("/performance-review/edit-objective/<id>", methods=['GET', 'POST'])
@login_required
def edit_objective(id):
    form = ObjectiveForm()
    if form.validate_on_submit():
        objective = Objective.objects(id=id).update(what=form.what.data, how=form.how.data)
        return redirect(url_for('frontend.performance_review'))
    else:
        edit_url = "/performance-review/edit-objective/%s" % id
        objective = Objective.objects(id=id).get()
        form.what.data = objective.what
        form.how.data = objective.how
        return render_template('add-objective.html', form=form, url=edit_url, edit=True)


@frontend.route('/profile/add-email', methods=['GET', 'POST'])
@login_required
def add_email():
    form = EmailForm()
    if form.validate_on_submit():
        email = form.data['email'].strip()
        current_user.other_email.append(email)
        current_user.save()
        message = "Sucessfully added email %s" % email
        flash(message)
        return redirect('/profile')
    else:
        return render_template('add-email.html', form=form)


@frontend.route('/performance-review/get-feedback')
@login_required
def feedback():
    return render_template('get-feedback.html')


@frontend.route('/performance-review/send-feedback-request', methods=['POST'])
@login_required
def send_feedback_request():
    recipients = request.json['recipients']
    for recipient in recipients:
        feedback_request = FeedbackRequest(requested_by=current_user._get_current_object())
        other_user = User.objects.filter(email=recipient).first()
        feedback_request.requested_from = other_user
        feedback_request.save()
        _send_feedback_email(feedback_request)
    return 'OK', 200


@frontend.route('/give-feedback/<id>', methods=['GET', 'POST'])
@login_required
def give_feedback(id):
    form = FeedbackForm()
    feedback_request = FeedbackRequest.objects(id=id).get()
    if form.validate_on_submit():
        feedback_request.feedback_details = form.feedback.data
        feedback_request.save()
        flash("Saved feedback")
        return redirect(url_for('frontend.view_feedback_given', id=id))
    else:
        return render_template('give-feedback.html', form=form, feedback_request=feedback_request)


# your requests for feedback from other people
@frontend.route('/performance-review/feedback')
@frontend.route('/performance-review/feedback/<id>')
@login_required
def requested_feedback(id=None):
    if id:
        feedback_request = FeedbackRequest.objects(id=id, requested_by=current_user._get_current_object()).get()
        return render_template('requested-feedback.html', feedback_request=feedback_request)
    else:
        feedback_requests = FeedbackRequest.objects(requested_by=current_user._get_current_object()).all()
        return render_template('requested-feedback.html', feedback_requests=feedback_requests)


def _send_feedback_email(feedback_request):
    host = current_app.config['HOST']
    if 'localhost' in host:
        host = "%s:8000" % host
    url = "http://%s/give-feedback/%s" % (host, feedback_request.id)
    html = render_template('email/feedback-request.html', request=feedback_request, url=url)
    msg = Message(html=html,
                  subject="Feeback request from test",
                  sender="noreply@csdigital.notrealgov.uk",
                  recipients=[feedback_request.requested_from.email])
    try:
        mail.send(msg)
        feedback_request.sent = True
        feedback_request.save()
    except Exception as ex:
        current_app.logger.error("failed to send email", ex)
        return 'Internal Server Error', 500
