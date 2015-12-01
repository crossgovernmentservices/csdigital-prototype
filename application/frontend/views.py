from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    jsonify
)

from flask.ext.security import login_required
from flask.ext.security.utils import login_user
from flask.ext.login import current_user


from application.frontend.forms import (
    LoginForm,
    EmailForm,
    ObjectiveForm,
)

from application.models import (
    User,
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
