from flask import (
    Blueprint,
    abort,
    jsonify,
    redirect,
    render_template,
    request,
    url_for)
from flask.ext.login import current_user
from flask.ext.security import login_required

from application.models import User


staff = Blueprint('staff', __name__, template_folder='templates')


def get_user_or_404(id):
    try:
        return User.objects.get(id=id)

    except User.DoesNotExist:
        abort(404)


def add_staff(**member_data):

    try:
        member = User.objects.get(**member_data)

    except User.DoesNotExist:
        abort(404)

    current_user.add_staff(member)


@staff.route('/staff', methods=['GET', 'POST'])
@login_required
def view():

    if request.is_xhr:

        if request.method == 'POST':
            add_staff(**request.get_json())

        return jsonify({'staff': list(current_user.staff)})

    return render_template('staff/view.html')


@staff.route('/staff/add', methods=['GET', 'POST'])
@login_required
def add():

    if request.method == 'POST':
        add_staff(**request.form.to_dict())
        return redirect(url_for('.view'))

    manager = current_user
    users = User.objects.filter(id__ne=manager.id)
    users = users.filter(id__nin=[member.id for member in manager.staff])

    return render_template('staff/add.html', users=users)
