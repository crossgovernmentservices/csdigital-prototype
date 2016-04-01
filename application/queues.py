import os
from socket import error as socket_error
from time import time

from kombu import Connection, Exchange, Queue
from kombu.pools import producers


exchange = Exchange('events', type='topic')
queue = Queue('userstore-prototype', exchange)
conn = Connection(os.environ.get('BROKER_URI'))


def publish_login(user):
    payload = {
        'entity': 'USER',
        'action': 'LOGIN',
        'user_id': user.email,
        'timestamp': time()}

    try:
        with producers[conn].acquire(block=True) as producer:
            producer.publish(payload, exchange=exchange)

    except socket_error:
        pass
