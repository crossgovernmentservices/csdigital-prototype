from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    url_for)
from flask.ext.login import current_user
from flask.ext.security import login_required
from mongoengine import Q

from application.models import Role, User
from application.utils import get_or_404


staff = Blueprint('staff', __name__, template_folder='templates')


def add_staff(**member_data):
    member = get_or_404(User, **member_data)
    current_user.add_staff(member)
    current_user.reload()


@staff.route('/staff')
@login_required
def view():
    return render_template('staff/view.html')


@staff.route('/staff.json')
@login_required
def staff_json():
    return jsonify({'staff': [u.to_json() for u in current_user.staff]})


def allowed_staff(manager):
    admin_role = Role.objects.get(name='ADMIN')
    users = User.objects.filter(
        id__nin=[member.id for member in manager.staff],
        id__ne=manager.id)
    if admin_role not in manager.roles:
        users = users.filter(
            roles__nin=[admin_role],
            manager=None)
    return users


@staff.route('/staff/add', methods=['GET', 'POST'])
@login_required
def add():

    if request.method == 'POST':
        if request.is_xhr:
            add_staff(**request.json)
            return view()

        else:
            add_staff(**request.form.to_dict())

        return redirect(url_for('.view'))

    users = allowed_staff(current_user)

    return render_template('staff/add.html', users=users)


@staff.route('/staff/search.json')
@login_required
def search():
    search_term = request.args.get('q')
    users = []

    if search_term:
        users = allowed_staff(current_user)
        users = users.filter(
            Q(email__icontains=search_term) |
            Q(full_name__icontains=search_term))
        users = users.order_by('full_name', 'email')

    return jsonify({'results': [
        {'name': u.full_name, 'value': str(u.id)} for u in users]})


@staff.route('/staff/<id>')
@login_required
def member(id):
    member = get_or_404(User, id=id)
    return render_template('staff/member.html', member=member)
