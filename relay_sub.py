#!/usr/bin/env python
import argparse
import util
import time
import sys
import json
import yaml
from cloud_tools import Subscriber
from relay import Relay


def my_callback(client, userdata, message):
    msg = json.loads(message.payload)
    relay.pulse()


if __name__ == "__main__":

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
    parser.add_argument("-i", "--clientID", help="Client ID", default='')
    parser.add_argument("-r", "--rootCA", help="Root CA file path", required=True)
    parser.add_argument("-c", "--cert", help="Certificate file path")
    parser.add_argument("-k", "--key", help="Private key file path")
    parser.add_argument("-t", "--topic", help="MQTT topic(s)", nargs='+', required=True)
    parser.add_argument("-p", "--pin", help="gpio pin (using BCM numbering)", type=int, required=True)
    parser.add_argument("-f", "--input_file", help="input file (yaml format)", default=None)
    args = parser.parse_args()

    relay = Relay(args.pin)
    relay.start()

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
        time.sleep(2)  # pause

    # Loop forever
    try:
        while True:
            time.sleep(0.2)  # sleep needed because CPU race
            pass
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
