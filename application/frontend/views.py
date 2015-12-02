from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    jsonify,
    current_app
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

from application.extensions import user_datastore

frontend = Blueprint('frontend', __name__, template_folder='templates')


@frontend.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@frontend.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.args.get('next'):
        form.next.data = request.args.get('next')
    if form.validate_on_submit():
        current_app.logger.info(form.data)
        email = form.email.data.strip()
        user = user_datastore.get_user(email)
        if not user:
            flash("You don't have a user account yet")
            return redirect(url_for('frontend.index'))
        login_user(user)
        #TODO check next is valid
        return redirect(form.next.data)
    return render_template('login.html', form=form)


@frontend.route('/profile')
@login_required
def profile():
    return render_template('profile.html')


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


@frontend.route('/objectives')
@login_required
def objectives():
    return render_template('objectives.html')


@frontend.route("/objectives/add", methods=['GET', 'POST'])
@login_required
def add_objective():
    form = ObjectiveForm()
    if form.validate_on_submit():
        message = 'Added objective'
        flash(message)
        objective = Objective(what=form.what.data, how=form.how.data)
        objective.save()
        current_user.objectives.add(objective)
        return redirect(url_for('frontend.objectives'))
    else:
        add_url = url_for('frontend.add_objective')
        return render_template('add-objective.html', form=form, url=add_url)


@frontend.route("/objectives/<id>", methods=['GET', 'POST'])
@login_required
def edit_objective(id):
    form = ObjectiveForm()
    if form.validate_on_submit():
        objective = Objective.objects(id=id).update(what=form.what.data, how=form.how.data)
        return redirect(url_for('frontend.objectives'))
    else:
        edit_url = url_for('frontend.edit_objective', id=id)
        objective = Objective.objects(id=id).get()
        form.what.data = objective.what
        form.how.data = objective.how
        return render_template('add-objective.html', form=form, url=edit_url, edit=True)


@frontend.route('/users.json')
@login_required
def users():
    q = request.args['q']
    users = User.objects.only('email').filter(email__icontains=q)
    return jsonify({'users': users})


