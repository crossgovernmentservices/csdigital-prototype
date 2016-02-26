import os

from flask.ext.assets import Bundle, Environment
import sass
from webassets.filter import Filter


class LibSass(Filter):
    name = 'libsass-output'
    options = {
        'output_style': 'SASS_OUTPUT_STYLE'
    }

    def __init__(self, include_paths=[], *args, **kwargs):
        super(LibSass, self).__init__(*args, **kwargs)
        self.include_paths = include_paths

    def _apply_sass(self, src):
        return sass.compile(
            string=src,
            output_style='expanded',
            include_paths=getattr(self, 'include_paths', []))

    def output(self, _in, out, **kwargs):
        out.write(self._apply_sass(_in.read()))

    def input(self, _in, out, **kwargs):
        out.write(_in.read())


cwd = os.path.dirname(__file__)


def static(*path):
    return os.path.join(cwd, 'static', *path)


libsass_output = LibSass(include_paths=[
    static('sass'),
    static('govuk_frontend_toolkit', 'stylesheets'),
    static('govuk_elements', 'public', 'sass', 'elements')])


env = Environment()


env.register('css_govuk_elements', Bundle(
    'sass/govuk_elements.scss',
    filters=(libsass_output,),
    output='stylesheets/govuk_elements.css',
    depends=[
        '/static/govuk_elements/public/sass/**/*.scss',
        '/static/govuk_frontend_toolkit/stylesheets/**/*.scss']))


env.register('css_main', Bundle(
    'sass/main.scss',
    filters=(libsass_output,),
    output='stylesheets/main.css',
    depends=[
        '/static/sass/main/**/*.scss',
        '/static/govuk_frontend_toolkit/stylesheets/**/*.scss']))


env.register('css_internal_interface', Bundle(
    'sass/internal_interface.scss',
    filters=(libsass_output,),
    output='stylesheets/internal_interface.css',
    depends=[
        '/static/sass/internal_interface/**/*.scss',
        '/static/govuk_frontend_toolkit/stylesheets/**/*.scss']))


env.register('css_journeys', Bundle(
    'sass/journeys.scss',
    filters=(libsass_output,),
    output='stylesheets/journeys.css',
    depends=['/static/sass/journeys/**/*.scss']))


env.register('css_hr', Bundle(
    'sass/hr.scss',
    filters=(libsass_output,),
    output='stylesheets/hr.css',
    depends=[
        '/static/sass/hr/**/*.scss',
        '/static/govuk_frontend_toolkit/stylesheets/**/*.scss']))
