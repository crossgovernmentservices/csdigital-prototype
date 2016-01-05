import os

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for
)
from flask.ext.security.utils import login_user

from application.extensions import user_datastore
from application.frontend.forms import LoginForm
from application.queues import SNSEventTopic
from application.sso import oidc


event_queue = SNSEventTopic(os.environ.get('SNS_TOPIC_NAME', 'EventsDev'))

sso = Blueprint('sso', __name__, url_prefix='/login')


@sso.context_processor
def sso_providers():
    return dict(sso_providers=current_app.config['OIDC'])


@sso.route('/', methods=['GET', 'POST'])
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

        # send login action to event queue
        event_queue.send('USER', 'LOGIN', email)

        # TODO check next is valid
        return redirect(form.next.data)

    return render_template('login.html', form=form)


@sso.route('/<provider>')
def login_provider(provider):
    session['provider'] = provider
    return redirect(current_app.oidc_client.login(provider))


@sso.route('/callback')
def oidc_callback():
    auth_code = request.args.get('code')
    provider = session['provider']
    user_info = current_app.oidc_client.authenticate(provider, auth_code)
    user = user_datastore.get_user(user_info['email'])

    if not user:
        flash("You don't have a user account yet: %s" % user_info['email'])
        return redirect(url_for('frontend.index'))

    login_user(user)

    event_queue.send('USER', 'LOGIN', user_info['email'])

    if 'next' in request.args:
        return redirect(request.args['next'])

    return redirect(url_for('frontend.index'))
