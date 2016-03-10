import credstash
from boto import utils, ec2

from application.config import Config


# get instance ID and AWS region
metadata = utils.get_instance_metadata()
instance_id = metadata['instance-id']
region = metadata['placement']['availability-zone'][:-1]

# get instance's environment name from AWS tag
conn = ec2.connect_to_region(region)
reservations = conn.get_all_instances(instance_ids=[instance_id])
env = reservations[0].instances[0].tags['Environment']
version = reservations[0].instances[0].tags['ConfigVersion']


def get_cred(name):
    table = "{}-credentials".format(env)
    return credstash.getSecret(name, version, region=region, table=table)


class AWSConfig(Config):
    SECRET_KEY = get_cred('SECRET_KEY')
    SECURITY_PASSWORD_HASH = get_cred('SECURITY_PASSWORD_HASH')
    MONGODB_SETTINGS = {
        'host': get_cred('MONGO_URI')
    }
    MAIL_SERVER = get_cred('MAILGUN_SMTP_SERVER')
    MAIL_PORT = get_cred('MAILGUN_SMTP_PORT')
    MAIL_USERNAME = get_cred('MAILGUN_SMTP_LOGIN')
    MAIL_PASSWORD = get_cred('MAILGUN_SMTP_PASSWORD')
    MAILGUN_API_KEY = get_cred('MAILGUN_API_KEY')
    HOST = get_cred('HOST')
    PORT = get_cred('PORT')
    EMAIL_DOMAIN = get_cred('EMAIL_DOMAIN')

    OIDC = {
        'auth0': {
            'domain': 'xgs.eu.auth0.com',
            'client': {
                'client_id': get_cred('AUTH0_CLIENT_ID'),
                'client_secret': get_cred('AUTH0_CLIENT_SECRET'),
                'redirect_uri': "http://{}:{}/login/callback".format(
                    HOST, PORT)
            }
        }
    }
