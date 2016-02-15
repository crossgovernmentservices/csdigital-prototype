# -*- coding: utf-8 -*-
'''The app module, containing the app factory function.'''

import os

from flask import Flask, render_template
from flask.ext.security import Security


def asset_path_context_processor():
    return {'asset_path': '/static/'}


def create_app(config=None):
    ''' An application factory, as explained here:
        http://flask.pocoo.org/docs/patterns/appfactories/
    '''
    app = Flask(__name__)

    if not config:
        config = os.environ.get('SETTINGS', 'application.config.Config')

    app.config.from_object(config)

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

    from application.feedback.views import feedback
    app.register_blueprint(feedback)

    from application.profile.views import profile
    app.register_blueprint(profile)

    from application.objectives.views import objectives
    app.register_blueprint(objectives)

    from application.mylog.views import mylog
    app.register_blueprint(mylog)

    from application.hatch.views import hatch
    app.register_blueprint(hatch)

    from application.journeys.views import journeys
    app.register_blueprint(journeys)

    from application.sso.views import sso
    app.register_blueprint(sso)

    from application.competency.views import competency
    app.register_blueprint(competency)

    from application.notes.views import notes
    app.register_blueprint(notes)

    from application.skills.views import skills
    app.register_blueprint(skills)

    from application.staff.views import staff
    app.register_blueprint(staff)


def register_extensions(app):
    from application.assets import env
    env.init_app(app)

    from flask.ext.mongoengine import MongoEngine
    db = MongoEngine()
    db.init_app(app)

    # flask security setup
    from application.extensions import user_datastore
    Security(app, user_datastore)

    # flask markdown
    from flaskext.markdown import Markdown
    Markdown(app)

    # flask mail
    from application.extensions import mail
    mail.init_app(app)

    import os
    if 'SENTRY_DSN' in os.environ:
        from raven.contrib.flask import Sentry
        Sentry(app, dsn=os.environ['SENTRY_DSN'])

    from application.sso.oidc import OIDC
    app.oidc_client = OIDC(app)

    if app.debug:
        from flask_debugtoolbar import DebugToolbarExtension
        DebugToolbarExtension().init_app(app)


def register_filters(app):
    def format_date(d):
        try:
            return d.strftime('%-d %B %Y')
        except Exception:
            return ''

    def format_entry(entry):
        out = []
        for field in entry._dynamic_fields:
            text = '%s : %s' % (field, getattr(entry, field))
            out.append(text)
        return '\n'.join(out)

    def initials(full_name):
      initials = ''.join(name[0].upper() for name in full_name.split())
      return initials

    def pluralise(number, singular = '', plural = 's'):
      if number == 1:
        return singular
      else:
        return plural

    app.jinja_env.filters['format_date'] = format_date
    app.jinja_env.filters['format_entry'] = format_entry
    app.jinja_env.filters['initials'] = initials
    app.jinja_env.filters['pluralise'] = pluralise
