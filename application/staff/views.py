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
from application.utils import get_or_404


staff = Blueprint('staff', __name__, template_folder='templates')


def add_staff(**member_data):
    member = get_or_404(User, **member_data)
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


@staff.route('/staff/<id>')
@login_required
def member(id):
    member = get_or_404(User, id=id)
    return render_template('staff/member.html', member=member)
