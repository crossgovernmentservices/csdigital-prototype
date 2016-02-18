import os

from application.factory import create_app
app = create_app(os.environ.get('SETTINGS', 'application.config.Config'))
