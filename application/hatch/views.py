from flask import (
    Blueprint,
    render_template,
)

from flask.ext.security.decorators import roles_required

from application.hatch.forms import AddUserForm

hatch = Blueprint('hatch', __name__, url_prefix='/the-hatch')

@hatch.route("/open")
@roles_required('ADMIN')
def hatch_open():
    return render_template('hatch/hatch.html')


@hatch.route("/add-user")
@roles_required('ADMIN')
def add_user():
    form = AddUserForm()
    if form.validate_on_submit():
        return "OK"
    return render_template('hatch/add_user.html', form=form)

