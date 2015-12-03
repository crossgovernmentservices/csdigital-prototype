from flask import (
    Blueprint,
    render_template,
    redirect,
    flash,
    url_for
)

from flask.ext.security import login_required
from flask.ext.login import current_user

from application.profile.forms import EmailForm

profile = Blueprint('profile', __name__, template_folder='templates')


@profile.route('/profile')
@login_required
def view_profile():
    return render_template('profile/profile.html')


@profile.route('/profile/add-email', methods=['GET', 'POST'])
@login_required
def add_email():
    form = EmailForm()
    if form.validate_on_submit():
        email = form.email.data.strip()
        current_user.other_email.append(email)
        current_user.save()
        message = "Sucessfully added email %s" % email
        flash(message)
        return redirect(url_for('profile.view_profile'))
    else:
        return render_template('profile/add-email.html', form=form)
