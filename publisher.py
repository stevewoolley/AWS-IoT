import logging
import util
import json
import argparse
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient


class Publisher:
    """A threaded Publisher object"""

    def __init__(self, endpoint, root_ca, key, cert, client_id='', log_level=logging.INFO):
        self.endpoint = endpoint
        self.root_ca = root_ca
        self.client_id = client_id
        self.client = None
        self.key = key
        self.cert = cert
        self.logger = util.set_logger(level=log_level)
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

if __name__ == "__main__":

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
    parser.add_argument("-i", "--clientID", help="Client ID", default='')
    parser.add_argument("-r", "--rootCA", help="Root CA file path", required=True)
    parser.add_argument("-c", "--cert", help="Certificate file path")
    parser.add_argument("-k", "--key", help="Private key file path")
    parser.add_argument("-t", "--topic", help="MQTT topic(s)", nargs='+', required=False)
    parser.add_argument("-s", "--source", help="source", default='message')
    parser.add_argument("-v", "--value", help="value", default='Hello world')
    parser.add_argument("-g", "--log_level", help="log level", type=int, default=logging.INFO)
    args = parser.parse_args()

for t in args.topic:
    Publisher(args.endpoint, args.rootCA, args.key, args.cert).publish(t, {args.source: args.value})
