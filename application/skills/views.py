from flask import (
    Blueprint,
    render_template,
    redirect,
    flash,
    url_for,
    request
)

from flask.ext.security import login_required
from flask.ext.login import current_user


skills = Blueprint('skills', __name__, template_folder='templates')


@skills.route('/skills')
@login_required
def audit():
    return render_template('skills/audit.html')