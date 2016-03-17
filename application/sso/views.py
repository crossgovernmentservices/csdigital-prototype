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
from flask.ext.security.utils import login_user, logout_user
import requests

from application.extensions import user_datastore
from application.frontend.forms import LoginForm
from application.models import make_inbox_email
from application.queues import publish_login


sso = Blueprint('sso', __name__, url_prefix='/login')


@sso.context_processor
def sso_providers():
    return dict(sso_providers=current_app.config['OIDC'])


@sso.app_context_processor
def auth0_logout():
    url = url_for('sso.logout')

    if 'auth0' in current_app.config['OIDC']:
        url = 'https://{host}/v2/logout?returnTo={returnTo}'.format(
            host=current_app.config['OIDC']['auth0']['domain'],
            returnTo=url_for('sso.logout', _external=True))

    return dict(logout_url=url)


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

        publish_login(user)

        # TODO check next is valid
        return redirect(form.next.data)

    return render_template('login.html', form=form)


@sso.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('frontend.index'))


@sso.route('/<provider>')
def login_provider(provider):
    session['provider'] = provider
    return redirect(current_app.oidc_client.login(
        provider,
        url_for('.oidc_callback', _external=True)))


def mapped_ids(user_id):
    id_mapper_url = 'http://localhost:5000/links/{}.json'.format(user_id)
    return requests.get(
        id_mapper_url,
        headers={'X-Requested-With': 'XMLHTTPRequest'}).json()


@sso.route('/callback')
def oidc_callback():
    auth_code = request.args.get('code')
    provider = session['provider']

    try:
        user_info = current_app.oidc_client.authenticate(
            provider,
            auth_code,
            url_for('.oidc_callback', _external=True))

    except Exception as e:
        flash('Login failed: {}: {}'.format(e.__class__.__name__, e), 'error')
        return redirect(url_for('frontend.index'))

    user = user_datastore.get_user(user_info['email'])

    if not user:
        # query identity mapping service for linked identities that may already
        # have an account
        for uid in mapped_ids(user_info['email'])['ids']:
            user = user_datastore.get_user(uid)
            if user:
                break

        if not user:
            # user has successfully logged in or registered on IdP
            # so create an account
            user = user_datastore.create_user(
                email=user_info['email'],
                inbox_email=make_inbox_email(user_info['email']),
                full_name=user_info.get('nickname', user_info.get('name')))
            user_role = user_datastore.find_or_create_role('USER')
            user_datastore.add_role_to_user(user, user_role)

    login_user(user)

    publish_login(user)

    if 'next' in request.args:
        return redirect(request.args['next'])

    return redirect(url_for('frontend.index'))
