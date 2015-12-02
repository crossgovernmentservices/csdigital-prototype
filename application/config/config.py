# -*- coding: utf-8 -*-
import os

class Config(object):
    APP_ROOT = os.path.abspath(os.path.dirname(__file__))
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_ROOT, os.pardir))
    WTF_CSRF_ENABLED = True
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SECURITY_PASSWORD_SALT = SECRET_KEY
    SECURITY_PASSWORD_HASH = os.environ.get('SECURITY_PASSWORD_HASH')
    MONGODB_SETTINGS = {
        'host': os.environ.get('MONGO_URI')
    }
    MAIL_SERVER = os.environ.get('MAILGUN_SMTP_SERVER')
    MAIL_PORT = os.environ.get('MAILGUN_SMTP_PORT')
    MAIL_USERNAME = os.environ.get('MAILGUN_SMTP_LOGIN')
    MAIL_PASSWORD = os.environ.get('MAILGUN_SMTP_PASSWORD')
    HOST = os.environ.get('HOST', 'localhost')

class DevelopmentConfig(Config):
    DEBUG = True
    WTF_CSRF_ENABLED = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'local-dev-not-secret')

class DockerConfig(DevelopmentConfig):
    # is this guaranteed to be up yet cause it's linked?
    host = os.environ.get('DB_PORT_27017_TCP_ADDR')
    port = int(os.environ.get('DB_PORT_27017_TCP_PORT', 27017))
    MONGODB_SETTINGS = {
        'host': host,
        'db': 'xgs_performance_reviews',
        'port': port
    }


class TestConfig(DockerConfig):
    TESTING = True
