# -*- coding: utf-8 -*-
'''The app module, containing the app factory function.'''
from flask import Flask, render_template

from flask.ext.security import Security

def asset_path_context_processor():
    return {'asset_path': '/static/'}


def create_app(config_filename):
    ''' An application factory, as explained here:
        http://flask.pocoo.org/docs/patterns/appfactories/
    '''
    app = Flask(__name__)
    app.config.from_object(config_filename)
    register_errorhandlers(app)
    register_blueprints(app)
    app.context_processor(asset_path_context_processor)
    register_extensions(app)
    register_filters(app)
    return app


def register_errorhandlers(app):
    def render_error(error):
        # If a HTTPException, pull the `code` attribute; default to 500
        error_code = getattr(error, 'code', 500)
        return render_template("{0}.html".format(error_code)), error_code
    for errcode in [401, 404, 500]:
        app.errorhandler(errcode)(render_error)
    return None


def register_blueprints(app):
    from application.frontend.views import frontend
    app.register_blueprint(frontend)

    from application.hatch.views import hatch
    app.register_blueprint(hatch)


def register_extensions(app):
    from application.assets import env
    env.init_app(app)

    from application.models import db
    db.init_app(app)

    # flask security setup
    from application.extensions import user_datastore
    security = Security(app, user_datastore)

    # flask markdown
    from flaskext.markdown import Markdown
    markdown = Markdown(app)

    # flask mail
    from application.extensions import mail
    mail.init_app(app)

    import os
    if 'SENTRY_DSN' in os.environ:
        from raven.contrib.flask import Sentry
        sentry = Sentry(app, dsn=os.environ['SENTRY_DSN'])


def register_filters(app):
    def format_date(d):
        try:
            return d.strftime('%-d %B %Y')
        except Exception as e:
            return ''

    app.jinja_env.filters['format_date'] = format_date

