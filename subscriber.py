#!/usr/bin/env python
import threading
import time
import logging
import util
import json
import argparse
import sys
import yaml
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient


def my_callback(client, userdata, message):
    msg = json.loads(message.payload)
    print("{} {} {}".format(util.now_string(), message.topic, msg))


class Subscriber(threading.Thread):
    """A threaded Subscriber object"""

    def __init__(self, endpoint, root_ca, key, cert, client_id='', log_level=logging.INFO):
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
        self.logger = util.set_logger(level=log_level)

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


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
    parser.add_argument("-i", "--clientID", help="Client ID", default='')
    parser.add_argument("-r", "--rootCA", help="Root CA file path", required=True)
    parser.add_argument("-c", "--cert", help="Certificate file path", required=True)
    parser.add_argument("-g", "--log_level", help="log level", type=int, default=logging.INFO)
    parser.add_argument("-k", "--key", help="Private key file path", required=True)
    parser.add_argument("-t", "--topic", help="MQTT topic(s)", nargs='+', required=True)
    parser.add_argument("-f", "--input_file", help="input file (yaml format)", default=None)
    args = parser.parse_args()

    subscriber = Subscriber(args.endpoint, args.rootCA, args.key, args.cert, args.clientID, args.log_level)

    if args.input_file is not None:
        f = open(args.input_file)
        topics = yaml.safe_load(f)
        for t in topics[args.endpoint]:
            print("Subscribing to {}".format(t))
            subscriber.subscribe(t, my_callback)
            time.sleep(2)  # pause between subscribes (maybe not needed?)

    for t in args.topic:
        print("Subscribing to {}".format(t))
        subscriber.subscribe(t, my_callback)
        time.sleep(2)  # pause between subscribes (maybe not needed?)

    # Loop forever
    try:
        while True:
            time.sleep(0.2)  # sleep needed because CPU race
            pass
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
