from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    current_app,
    flash,
    request,
    jsonify
)

from flask.ext.security import login_required
from flask.ext.security.utils import login_user
from flask.ext.login import current_user

from application.frontend.forms import LoginForm
from application.models import (
    User,
    Objectives
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
    return render_template('performance_review.html')


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


@frontend.route('/feedback-request.json', methods=['POST'])
@login_required
def feedback_request():
    current_app.logger.info(request.json)
    return 'OK'
