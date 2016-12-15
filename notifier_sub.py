#!/usr/bin/env python

import argparse
import time
import sys
from cloud_tools import Subscriber
import yaml
import json
from pync import Notifier


def my_callback(client, userdata, message):
    msg = json.loads(message.payload)
    if 'source' in msg:
        Notifier.notify(msg['message'], title=msg['source'])
    elif 'message' in msg:
        Notifier.notify(msg['message'])


if __name__ == "__main__":

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
    parser.add_argument("-i", "--clientID", help="Client ID",
                        default='')  # empty string auto generates unique client ID
    parser.add_argument("-r", "--rootCA", help="Root CA file path", required=True)
    parser.add_argument("-c", "--cert", help="Certificate file path")
    parser.add_argument("-k", "--key", help="Private key file path")
    parser.add_argument("-t", "--topic", help="MQTT topic(s)", nargs='+', required=False)
    parser.add_argument("-f", "--input_file", help="input file (yaml format)", default=None)
    args = parser.parse_args()

    subscriber = Subscriber(args.endpoint, args.rootCA, args.key, args.cert, args.clientID)

    # Load configuration file
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
