from flask import (
    Blueprint,
    render_template,
    url_for,
    redirect,
    flash,
    current_app,
    request
)

from flask.ext.security.decorators import roles_required
from flask.ext.login import current_user

from application.models import (
    User,
    Objectives,
    Objective
)

hatch = Blueprint('hatch', __name__, url_prefix='/the-hatch')

@hatch.route("/open")
@roles_required('ADMIN')
def hatch_open():
    return render_template('hatch/hatch.html')


@hatch.route("/manage-user")
@roles_required('ADMIN')
def manage_user():
    users = User.objects
    return render_template('hatch/manage_user.html', users=users)


@hatch.route("/your-stuff")
@roles_required('ADMIN')
def your_stuff():
    return render_template('hatch/your_stuff.html')


@hatch.route("/<email>/start-objectives")
@roles_required('ADMIN')
def start_objectives(email):
    user= User.objects.filter(email=email).first()
    objectives = Objectives()
    objectives.save()
    user.objectives = objectives
    user.save()
    message = "Objectives started with start date %s" % user.objectives.started_on
    flash(message)
    return redirect(url_for('hatch.manage_user'))


@hatch.route("/add-objective", methods=['POST'])
@roles_required('ADMIN')
def add_objective():
    what = request.form['what']
    how = request.form['how']
    objective = Objective(what=what, how=how)
    objective.save()
    current_user.objectives.add(objective)
    return 'Created objective for ' + current_user.email

