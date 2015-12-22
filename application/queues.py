import socket
from time import time

from kombu import Connection

from flask import current_app


class EventQueue(object):
    def __init__(self, broker_uri, queue_name='event_queue', serializer='json',
                 compression=None):
        self.broker_uri = broker_uri
        self.queue_name = queue_name
        self.serializer = serializer
        self.compression = compression

    def send(self, entity, action, context={}):
        with Connection(self.broker_uri) as conn:
            try:
                queue = conn.SimpleQueue(self.queue_name,
                                         exchange_opts={'type': 'topic'})
            except conn.connection_errors as err:
                current_app.logger.warning(
                    'Broker connection failed with: %s', err)
                return

            queue.put({
                'entity': entity,
                'action': action,
                'context': context,
                'hostname': socket.gethostname(),
                'timestamp': time()
            }, serializer=self.serializer, compression=self.compression)
