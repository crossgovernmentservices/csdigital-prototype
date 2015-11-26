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

from application.frontend.forms import (
    LoginForm,
    EmailForm,
    ObjectiveForm
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
    if current_user and current_user.is_authenticated():
        return redirect('/profile')
    form = LoginForm()
    if form.validate_on_submit():
        email = form.data['email'].strip()
        user = current_app.extensions['user_datastore'].get_user(email)
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


@frontend.route('/performance-review/feedback')
@login_required
def feedback():
    return render_template('feedback.html')


@frontend.route('/users.json')
@login_required
def users():
    q = request.args['q']
    users = User.objects.only('email').filter(email__icontains=q)
    return jsonify({'users': users})


@frontend.route('/performance-review/feedback-request', methods=['POST'])
@login_required
def feedback_request():
    current_app.logger.info(request.json)
    recipients = request.json['recipients']
    #TODO send email to each of the recipients
    for recipient in recipients:
        feedback_request = FeedbackRequest(recipient_email=recipient)
        current_user.add_request_if_not_present(feedback_request)
        current_user.save()
    return 'OK', 200


@frontend.route("/performance-review/add-objective", methods=['GET','POST'])
@login_required
def add_objective():
    form = ObjectiveForm()
    if form.validate_on_submit():
        message = 'Added objective'
        flash(message)
        objective = Objective(what=form.what.data, how=form.how.data)
        current_user.objectives.add(objective)
        return redirect(url_for('frontend.performance_review'))
    else:
        return render_template('add-objective.html', form=form)



@frontend.route('/profile/add-email', methods=['GET','POST'])
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
