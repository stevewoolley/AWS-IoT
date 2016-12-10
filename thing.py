import threading
import time
import json
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient


class Thing(threading.Thread):
    """A threaded IoT Thing object"""

    STATE = 'state'
    REPORTED = 'reported'
    DESIRED = 'desired'
    TIMEOUT = 'timeout'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'

    def __init__(self, name, endpoint, root_ca, key, cert, web_socket=False):
        threading.Thread.__init__(self)
        self.name = name
        self.client = None
        self.connected = False
        self.endpoint = endpoint
        self.web_socket = web_socket
        self.root_ca = root_ca
        self.key = key
        self.cert = cert
        self.finish = False
        self.daemon = True
        self.shadow = None
        self.status = None
        self.properties = None
        self.client_id = ''
        self.last_update = None
        self.last_refresh = None
        self.refresh()

    def connect(self):
        # Setup
        if self.web_socket:
            self.client = AWSIoTMQTTShadowClient(self.client_id, useWebsocket=True)
            self.client.configureEndpoint(self.endpoint, 443)
            self.client.configureCredentials(self.root_ca)
        else:
            self.client = AWSIoTMQTTShadowClient(self.client_id)
            self.client.configureEndpoint(self.endpoint, 8883)
            self.client.configureCredentials(self.root_ca, self.key, self.cert)
        self.client.configureConnectDisconnectTimeout(10)  # 10 sec
        self.client.configureMQTTOperationTimeout(5)  # 5 sec
        # Connect
        self.connected = self.client.connect()
        self.shadow = self.client.createShadowHandlerWithName(self.name, True)

    def custom_shadow_callback_update(self, payload, response_status, token):
        if response_status == self.ACCEPTED:
            msg = json.loads(payload)
            self.last_update = msg['timestamp']

    def update(self, properties, state=REPORTED):
        if not self.connected:
            self.connect()
        payload = {self.STATE: {state: {}}}
        payload[self.STATE][state] = properties
        self.shadow.shadowUpdate(json.dumps(payload), self.custom_shadow_callback_update, 30)

    def custom_shadow_callback_get(self, payload, response_status, token):
        if response_status == self.ACCEPTED:
            self.properties = payload
            msg = json.loads(payload)
            self.last_refresh = msg['timestamp']

    def refresh(self):
        print("A")
        if not self.connected:
            self.connect()
        print("B")
        self.shadow.shadowGet(self.custom_shadow_callback_get, 30)
        print("C")

    def run(self):
        while not self.finish:
            time.sleep(0.001)
