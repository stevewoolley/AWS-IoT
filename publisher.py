import logging
import util
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient


class Publisher:
    """A threaded Publisher object"""

    def __init__(self, endpoint, root_ca, key, cert, client_id='', web_socket=False, log_level=logging.INFO):
        self.endpoint = endpoint
        self.root_ca = root_ca
        self.client_id = client_id
        self.client = None
        self.web_socket = web_socket
        self.key = key
        self.cert = cert
        self.logger = util.set_logger(level=log_level)
        self.connected = False

    def connect(self):
        # Setup
        if self.web_socket:
            self.client = AWSIoTMQTTClient(self.client_id, useWebsocket=True)
            self.client.configureEndpoint(self.endpoint, 443)
            self.client.configureCredentials(self.root_ca)
        else:
            self.client = AWSIoTMQTTClient(self.client_id)
            self.client.configureEndpoint(self.endpoint, 8883)
            self.client.configureCredentials(self.root_ca, self.key, self.cert)
        self.client.configureAutoReconnectBackoffTime(1, 32, 20)
        self.client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        self.client.configureDrainingFrequency(2)  # Draining: 2 Hz
        self.client.configureConnectDisconnectTimeout(10)  # 10 sec
        self.client.configureMQTTOperationTimeout(5)  # 5 sec
        # Connect
        self.connected = self.client.connect()

    def publish(self, topic, obj, qos=0):
        if not self.connected:
            self.connect()
        self.client.publish(topic, obj, qos)

    def publish_multiple(self, objects, qos=0):
        if not self.connected:
            self.connect()
        for obj in objects:
            self.client.publish(obj['topic'], obj['payload'], qos)
