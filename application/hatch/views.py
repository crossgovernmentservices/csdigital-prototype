from flask import (
    Blueprint,
    render_template,
)

from flask.ext.security.decorators import roles_required

hatch = Blueprint('hatch', __name__, url_prefix='/the-hatch')

@hatch.route("/open")
@roles_required('ADMIN')
def hatch_open():
    return render_template('hatch/hatch.html')
