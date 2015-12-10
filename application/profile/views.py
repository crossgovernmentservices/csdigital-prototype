from flask import (
    Blueprint,
    render_template,
    redirect,
    flash,
    url_for,
    current_app,
    request
)

from flask.ext.security import login_required
from flask.ext.login import current_user

from application.profile.forms import EmailForm, UpdateDetailsForm

profile = Blueprint('profile', __name__, template_folder='templates')


@profile.route('/profile')
@login_required
def view_profile():
    return render_template('profile/profile.html')


@profile.route('/profile/add-email', methods=['GET', 'POST'])
@login_required
def add_email():
    form = EmailForm()
    user = current_user
    if form.validate_on_submit():
        email = form.email.data.strip()
        if email not in user.other_email and email != user.email:
            user.other_email.append(email)
            user.save()
            message = "Sucessfully added email %s" % email
        else:
            message = "Already have email: %s" % email
        flash(message)
        return redirect(url_for('profile.view_profile'))
    else:
        return render_template('profile/add-email.html', form=form)


@profile.route('/profile/remove-email')
@login_required
def remove_email():
    email = request.args.get('email')
    user = current_user
    if email:
        email = email.strip()
        user.other_email.remove(email)
        user.save()
        message = "Removed email: %s" % email
        flash(message)
    return redirect(url_for('profile.view_profile'))

@profile.route('/profile/update-details')
@login_required
def update_details():
  form = UpdateDetailsForm()
  return render_template('profile/update-details.html', form=form)
