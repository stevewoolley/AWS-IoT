import argparse
import logging
import time
import util
import sys
from subscriber import Subscriber
import json


def my_callback(client, userdata, message):
    print("%s %s %s" % (util.now_string(), message.topic, message.payload))
    msg = json.loads(message.payload)
    if msg.has_key('alert_count'):
        print("%s alert_count %s" % (util.now_string(), msg['alert_count']))


# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
parser.add_argument("-i", "--clientID", help="Client ID", default='')  # empty string auto generates unique client ID
parser.add_argument("-r", "--rootCA", help="Root CA file path", required=True)
parser.add_argument("-c", "--cert", help="Certificate file path")
parser.add_argument("-k", "--key", help="Private key file path")
parser.add_argument("-g", "--log_level", help="log level", type=int, default=logging.INFO)
parser.add_argument("-t", "--topic", help="MQTT topic(s)", nargs='+', required=True)
args = parser.parse_args()

subscriber = Subscriber(
    args.endpoint,
    args.rootCA,
    args.key,
    args.cert
)
for t in args.topic:
    print("%s subscribe to %s" % (util.now_string(), t))
    subscriber.subscribe(t, my_callback)
    time.sleep(2)  # pause between subscribes (maybe not needed?)

# Loop forever
try:
    while True:
        time.sleep(0.2)  # sleep needed because CPU race
        pass
except (KeyboardInterrupt, SystemExit):
    sys.exit()
