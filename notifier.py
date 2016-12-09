#!/usr/bin/env python
import argparse
import logging
import time
import sys
from subscriber import Subscriber
import yaml
import json
from pync import Notifier


def my_callback(client, userdata, message):
    msg = json.loads(message.payload)
    if msg['source']:
        Notifier.notify(msg['message'], title=msg['source'])
    else:
        Notifier.notify(msg['message'])


# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
parser.add_argument("-i", "--clientID", help="Client ID", default='')  # empty string auto generates unique client ID
parser.add_argument("-r", "--rootCA", help="Root CA file path", required=True)
parser.add_argument("-c", "--cert", help="Certificate file path")
parser.add_argument("-k", "--key", help="Private key file path")
parser.add_argument("-g", "--log_level", help="log level", type=int, default=logging.INFO)
parser.add_argument("-y", "--config_file", help="config file (yaml format)", default='notifier.yml')
args = parser.parse_args()

# Load configuration file
f = open(args.config_file)
topics = yaml.safe_load(f)

subscriber = Subscriber(
    args.endpoint,
    args.rootCA,
    args.key,
    args.cert
)

for topic in topics[args.endpoint]:
    print("Subscribing to: %s" % topic)
    subscriber.subscribe(topic, my_callback)
    time.sleep(2)  # pause between subscribes (maybe not needed?)

# Loop forever
try:
    while True:
        time.sleep(0.2)  # sleep needed because CPU race
        pass
except (KeyboardInterrupt, SystemExit):
    sys.exit()
