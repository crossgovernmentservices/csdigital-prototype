import socket
from time import time

from kombu import Connection, Exchange
from kombu.pools import producers

from flask import current_app


class EventQueue(object):
    def __init__(self, broker_uri, serializer='json', compression=None):
        self.exchange = Exchange('events', 'topic', durable=True)
        self.broker_uri = broker_uri
        self.serializer = serializer
        self.compression = compression

    def send(self, entity, action, context={}):
        with Connection(self.broker_uri) as conn:
            payload = {
                'entity': entity,
                'action': action,
                'context': context,
                'hostname': socket.gethostname(),
                'timestamp': time()
            }

            try:
                with producers[conn].acquire(block=True) as producer:
                    producer.publish(payload, serializer=self.serializer,
                                     compression=self.compression,
                                     exchange=self.exchange,
                                     declare=[self.exchange])

                    current_app.logger.info('Event sent: entity=%s, action=%s',
                                            entity, action)
            except conn.connection_errors as err:
                current_app.logger.warning(
                    'Broker connection failed with: %s', err)
                return
