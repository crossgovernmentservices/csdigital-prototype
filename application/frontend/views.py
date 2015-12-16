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

from application.frontend.forms import LoginForm

from application.models import User

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
        # TODO check next is valid
        return redirect(form.next.data)
    return render_template('login.html', form=form)


@frontend.route('/users.json')
@login_required
def users():
    q = request.args['q']
    users = User.objects.only('email').filter(email__icontains=q)
    return jsonify({'users': users})
