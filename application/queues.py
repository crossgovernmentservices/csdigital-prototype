import socket
import json
from time import time

from kombu import Connection, Exchange
from kombu.pools import producers

from flask import current_app


class EventExchange(object):
    def __init__(self, broker_uri, exchange_name, serializer='json',
                 compression=None):
        self.exchange = Exchange(exchange_name, 'topic', durable=True)
        self.broker_uri = broker_uri
        self.serializer = serializer
        self.compression = compression

    def send(self, entity, action, user_id, context={}):
        with Connection(self.broker_uri) as conn:
            payload = {
                'entity': entity,
                'action': action,
                'user_id': user_id,
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


class SNSEventTopic(object):
    def __init__(self, name):
        import boto3

        self.sns = boto3.client('sns')

        resp = self.sns.create_topic(Name=name)
        self.arn = resp['TopicArn']

    def send(self, entity, action, user_id, context={}):
        payload = {
            'entity': entity,
            'action': action,
            'user_id': user_id,
            'context': context,
            'hostname': socket.gethostname(),
            'timestamp': time()
        }

        resp = self.sns.publish(
            TopicArn=self.arn,
            Message=json.dumps(payload)
        )

        current_app.logger.info(
            'Event sent: MessageId=%s, entity=%s, action=%s',
            resp['MessageId'], entity, action)
