import argparse
import logging
import time
import datetime
import sys
from subscriber import Subscriber
import json


def my_callback(client, userdata, message):
    print("%s %s %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), message.topic, message.payload))
    msg = json.loads(message.payload)
    if msg.has_key('alert_count'):
        print("%s alert_count %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), msg['alert_count']))


# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
parser.add_argument("-i", "--clientID", help="Client ID", default='')  # empty string auto generates unique client ID
parser.add_argument("-r", "--rootCA", help="Root CA file path", required=True)
parser.add_argument("-c", "--cert", help="Certificate file path")
parser.add_argument("-k", "--key", help="Private key file path")
parser.add_argument("-g", "--log_level", help="log level", type=int, default=logging.INFO)
parser.add_argument("-t", "--topic", help="MQTT topic")
args = parser.parse_args()

print("%s subscribe to %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), args.topic))
subscriber = Subscriber(
    args.endpoint,
    args.rootCA,
    args.key,
    args.cert
)
subscriber.subscribe(args.topic, my_callback)
time.sleep(2)  # pause between subscribes (maybe not needed?)
print("%s subscribed to %s" % (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), args.topic))

# Loop forever
try:
    while True:
        time.sleep(0.2)  # sleep needed because CPU race
        pass
except (KeyboardInterrupt, SystemExit):
    sys.exit()
