from flask import (
    Blueprint,
    render_template
)

from flask.ext.security import login_required

mylog = Blueprint('mylog', __name__, template_folder='templates')


@mylog.route('/my-log')
@login_required
def view_mylog():
    return render_template('mylog/log.html')
