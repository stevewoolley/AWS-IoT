import threading
import time
import logging
import util
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient


class Subscriber(threading.Thread):
    """A threaded Subscriber object"""

    def __init__(self, endpoint, root_ca, key, cert, client_id='', name='subscriber', web_socket=False,
                 log_level=logging.INFO):
        threading.Thread.__init__(self)
        self.name = name
        self.endpoint = endpoint
        self.web_socket = web_socket
        self.client_id = client_id
        self.root_ca = root_ca
        self.key = key
        self.cert = cert
        self.client = None
        self.finish = False
        self.daemon = True
        self.connected = False
        self.logger = util.set_logger(level=log_level)
        self.last_reading = None

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
        self.client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        self.client.configureConnectDisconnectTimeout(10)  # 10 sec
        self.client.configureMQTTOperationTimeout(5)  # 5 sec
        # Connect
        self.connected = self.client.connect()

    def subscribe(self, topic, callback, qos=1):
        if not self.connected:
            self.connect()
        self.client.subscribe(topic, qos, callback)

    def run(self):
        while not self.finish:
            time.sleep(0.001)
