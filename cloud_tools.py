import json
import boto3
import ssl
import logging
import paho.mqtt.publish as publish


class Publisher:
    """A Publisher object"""
    STATE = 'state'
    REPORTED = 'reported'
    DESIRED = 'desired'

    def __init__(self,
                 endpoint,
                 root_ca,
                 key,
                 cert,
                 port=8883,
                 keepalive=60,
                 clientID=None,
                 tls_version=ssl.PROTOCOL_SSLv23
                 ):
        self._endpoint = endpoint
        self._port = port
        self._keep_alive = keepalive
        self._clientID = clientID
        self._log = logging.getLogger(__name__)
        self._tls_dict = {'ca_certs': root_ca,
                          'certfile': cert,
                          'keyfile': key,
                          'tls_version': tls_version}
        self._log.debug("publisher init")

    def publish(self, topic, payload, qos=0, retain=False):
        self._log.debug("publish {} {}".format(topic, payload))
        publish.single(topic,
                       payload=json.dumps(payload),
                       qos=qos,
                       retain=retain,
                       hostname=self._endpoint,
                       port=self._port,
                       client_id=self._clientID,
                       keepalive=self._keep_alive,
                       tls=self._tls_dict
                       )

    def report(self, topic, payload, state=REPORTED, qos=0, retain=False):
        self.publish(topic, {self.STATE: {state: payload}}, qos=qos, retain=retain)


class Reporter:
    """An AWS Reporter"""

    # constants
    STATE = 'state'
    REPORTED = 'reported'
    DESIRED = 'desired'
    TIMEOUT = 'timeout'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    TIMESTAMP = 'timestamp'
    CLIENT_TOKEN = 'clientToken'
    VERSION = 'version'
    METADATA = 'metadata'
    PAYLOAD = 'payload'

    def __init__(self, name):
        self.name = name
        self._client = boto3.client('iot-data')
        self._shadow = {}
        self.properties = {}
        self.metadata = {}
        self.last_report = None
        self.last_refresh = None
        self.version = None
        # set initial shadow
        self.refresh()

    def refresh(self):
        # query
        response = self._client.get_thing_shadow(thingName=self.name)
        self._shadow = json.loads(response[self.PAYLOAD].read().decode('utf-8'))
        # set properties
        if self.TIMESTAMP in self._shadow:
            self.last_refresh = self._shadow[self.TIMESTAMP]
        if self.STATE in self._shadow:
            if self.REPORTED in self._shadow[self.STATE]:
                self.properties = self._shadow[self.STATE][self.REPORTED]
        if self.METADATA in self._shadow:
            if self.REPORTED in self._shadow[self.METADATA]:
                self.metadata = self._shadow[self.METADATA][self.REPORTED]
                for k, v in self.metadata.iteritems():
                    if v[self.TIMESTAMP] is None or v[self.TIMESTAMP] > self.last_report:
                        self.last_report = v[self.TIMESTAMP]
        if self.VERSION in self._shadow:
            self.version = self._shadow[self.VERSION]

    def put(self, state, obj):
        payload = {self.STATE: {state: obj}}
        for k, v in obj.iteritems():
            payload[self.STATE][state][k] = v
        self._client.update_thing_shadow(thingName=self.name, payload=json.dumps(payload))
