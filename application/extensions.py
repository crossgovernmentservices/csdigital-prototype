from flask.ext.mail import Mail, email_dispatched
from flask.ext.security import MongoEngineUserDatastore

from application.models import (
    db,
    User,
    Role
)


user_datastore = MongoEngineUserDatastore(db, User, Role)

mail = Mail()


def log_message(message, app):
    app.logger.debug(message.as_string())

email_dispatched.connect(log_message)
