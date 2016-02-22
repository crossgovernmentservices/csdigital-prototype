from flask import (
    Blueprint,
    redirect,
    render_template,
    url_for
)
from flask.ext.login import current_user
from flask.ext.security import login_required


hr = Blueprint('hr', __name__, template_folder='templates')


@hr.route('/hr/capability')
@hr.route('/hr')
def index():
    return render_template('hr/capability.html', current="capability")

@hr.route('/hr/professions')
def professions():
    return render_template('hr/professions.html', current="professions")

@hr.route('/hr/competency')
def competency():
    return render_template('hr/competency.html', current="competency")

@hr.route('/hr/performance')
def performance():
    return render_template('hr/performance.html', current="performance")
