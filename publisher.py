import logging
import util
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient


class Publisher:
    """A Publisher object"""

    def __init__(self, endpoint, root_ca, key, cert, client_id='', web_socket=False,
                 log_level=logging.INFO):
        self.endpoint = endpoint
        self.web_socket = web_socket
        self.client_id = client_id
        self.root_ca = root_ca
        self.key = key
        self.cert = cert
        self.client = None
        self.connected = False
        self.logger = util.set_logger(level=log_level)

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

    def publish(self, topic, message, qos=1):
        if not self.connected:
            self.connect()
        self.client.publish(topic, message, qos)
        self.connected = not self.client.disconnect()