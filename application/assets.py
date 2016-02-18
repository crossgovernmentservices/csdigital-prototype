import os

from flask_assets import Bundle, Environment
from webassets.filter import get_filter


scss = get_filter('scss', as_output=True)
cwd = os.path.dirname(__file__)


def static(*path):
    return os.path.join(cwd, 'static', *path)


scss.load_paths = [
    static('sass'),
    static('govuk_frontend_toolkit/stylesheets'),
    static('govuk_elements/public/sass/elements')]


css_govuk_elements = Bundle(
    'sass/govuk_elements.scss',
    filters=scss,
    output='stylesheets/govuk_elements.css',
    depends=[
        '/static/govuk_elements/public/sass/**/*.scss',
        '/static/govuk_frontend_toolkit/stylesheets/**/*.scss'])

css_internal_interface = Bundle(
    'sass/internal_interface.scss',
    filters=scss,
    output='stylesheets/internal_interface.css',
    depends=[
        '/static/sass/internal_interface/**/*.scss',
        '/static/govuk_frontend_toolkit/stylesheets/**/*.scss'])

css_main = Bundle(
    'sass/main.scss',
    filters=scss,
    output='stylesheets/main.css',
    depends=[
        '/static/sass/main/**/*.scss',
        '/static/govuk_frontend_toolkit/stylesheets/**/*.scss'])

css_journeys = Bundle(
    'sass/journeys.scss',
    filters=scss,
    output='stylesheets/journeys.css',
    depends=['/static/sass/journeys/**/*.scss'])

env = Environment()
env.register('css_govuk_elements', css_govuk_elements)
env.register('css_main', css_main)
env.register('css_internal_interface', css_internal_interface)
env.register('css_journeys', css_journeys)
