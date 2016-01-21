from flask import (
    Blueprint,
    render_template)
from flask.ext.security import login_required


staff = Blueprint('staff', __name__, template_folder='templates')


@staff.route('/staff')
@login_required
def view():
    return render_template('staff/view.html')
