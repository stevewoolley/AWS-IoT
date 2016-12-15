import json
import threading
import time
import boto3
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient


class Publisher:
    """A threaded Publisher object"""

    def __init__(self, endpoint, root_ca, key, cert, client_id=''):
        self.endpoint = endpoint
        self.root_ca = root_ca
        self.client_id = client_id
        self.client = None
        self.key = key
        self.cert = cert
        self.connected = False

    def connect(self):
        # Setup
        self.client = AWSIoTMQTTClient(self.client_id)
        self.client.configureEndpoint(self.endpoint, 8883)
        self.client.configureCredentials(self.root_ca, self.key, self.cert)
        self.client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        self.client.configureConnectDisconnectTimeout(10)  # 10 sec
        self.client.configureMQTTOperationTimeout(5)  # 5 sec
        # Connect
        self.connected = self.client.connect()

    def publish(self, topic, obj, qos=0):
        if not self.connected:
            self.connect()
        msg = json.dumps(obj)
        self.client.publish(topic, msg, qos)


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
        # Setup
        self._client = AWSIoTMQTTClient(self.client_id)
        self._client.configureEndpoint(self.endpoint, 8883)
        self._client.configureCredentials(self.root_ca, self.key, self.cert)
        self._client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        self._client.configureConnectDisconnectTimeout(10)  # 10 sec
        self._client.configureMQTTOperationTimeout(5)  # 5 sec
        # Connect
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
        payload = {self.STATE: {state: {}}}
        for k, v in obj.iteritems():
            payload[self.STATE][state][k] = v
        self._client.update_thing_shadow(thingName=self.name, payload=json.dumps(payload))
