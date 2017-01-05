import json
import boto3
import ssl
import logging
import paho.mqtt.publish as publish
import threading
import time
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient


class Publisher:
    """A Publisher object"""
    STATE = 'state'
    REPORTED = 'reported'
    DESIRED = 'desired'
    THING_SHADOW = "$aws/things/{}/shadow/update"
    DATE_FORMAT = '%Y/%m/%d %-I:%M %p %Z'

    def __init__(self,
                 endpoint,
                 root_ca,
                 key,
                 cert,
                 port=8883,
                 keepalive=60,
                 clientID=None,
                 tls_version=ssl.PROTOCOL_SSLv23,
                 log_level=logging.WARNING
                 ):
        self._endpoint = endpoint
        self._port = port
        self._keepalive = keepalive
        self._clientID = clientID
        self._tls_version = tls_version
        logging.basicConfig(level=log_level)
        self._logger = logging.getLogger(__name__)
        self._tls = {'ca_certs': root_ca, 'certfile': cert, 'keyfile': key, 'tls_version': tls_version, 'ciphers': None}

    def report(self, topic, payload, qos=0, retain=False):
        publish.single(topic, payload=json.dumps(payload), qos=qos, retain=False, hostname=self._endpoint,
                       port=self._port,
                       client_id=self._clientID, keepalive=self._keepalive, auth=None, tls=self._tls)


class Subscriber(threading.Thread):
    """A threaded Subscriber object"""

    def __init__(self, endpoint, root_ca, key, cert, client_id=''):
        threading.Thread.__init__(self)
        self.endpoint = endpoint
        self.client_id = client_id
        self.root_ca = root_ca
        self.key = key
        self.cert = cert
        self._client = None
        self.finish = False
        self.daemon = True
        self.connected = False

    def connect(self):
        self._client = AWSIoTMQTTClient(self.client_id)
        self._client.configureEndpoint(self.endpoint, 8883)
        self._client.configureCredentials(self.root_ca, self.key, self.cert)
        self._client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        self._client.configureConnectDisconnectTimeout(10)  # 10 sec
        self._client.configureMQTTOperationTimeout(5)  # 5 sec
        self.connected = self._client.connect()

    def subscribe(self, topic, callback, qos=1):
        if not self.connected:
            self.connect()
        self._client.subscribe(topic, qos, callback)

    def run(self):
        while not self.finish:
            time.sleep(0.001)


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
