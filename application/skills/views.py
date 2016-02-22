from flask import (
    Blueprint,
    redirect,
    render_template,
    url_for
)
from flask.ext.login import current_user
from flask.ext.security import login_required

from application.skills.forms import AuditForm
from application.skills.models import Audit


skills = Blueprint('skills', __name__, template_folder='templates')


@skills.route('/skills', methods=['GET', 'POST'])
@login_required
def audit():
    form = AuditForm()
    user = current_user._get_current_object()

    if form.validate_on_submit():
        audit = Audit.objects.create(
            owner=user,
            **form.data)
        return redirect(url_for('.audit'))

    else:
        audit = Audit.objects.filter(owner=user).order_by('-created_date').first()

    form = AuditForm(obj=audit)
    return render_template('skills/audit.html', form=form)
