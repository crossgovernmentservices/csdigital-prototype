from flask import (
    Blueprint,
    redirect,
    render_template,
    url_for
)
from flask.ext.login import current_user
from flask.ext.security import login_required


hr = Blueprint('hr', __name__, template_folder='templates')


@hr.route('/hr')
def index():
    return render_template('hr/capability.html')

@hr.route('/hr/professions')
def professions():
    return render_template('hr/professions.html', current="professions")
