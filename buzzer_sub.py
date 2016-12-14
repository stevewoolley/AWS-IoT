#!/usr/bin/env python
import argparse
import logging
import util
import time
import sys
import json
import yaml
from subscriber import Subscriber
from buzzer import Buzzer


def my_callback(client, userdata, message):
    msg = json.loads(message.payload)
    c = args.beep_count
    if 'alert_count' in msg:
        c = msg['alert_count']
    buzzer.beep(beep_duration=args.beep_duration, quiet_duration=args.quiet_duration, count=c)
    logger.info("buzzer {}".format(c))

if __name__ == "__main__":

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
    parser.add_argument("-i", "--clientID", help="Client ID", default='')  # empty string auto generates unique client ID
    parser.add_argument("-r", "--rootCA", help="Root CA file path", required=True)
    parser.add_argument("-c", "--cert", help="Certificate file path")
    parser.add_argument("-k", "--key", help="Private key file path")
    parser.add_argument("-t", "--topic", help="MQTT topic(s)", nargs='+', required=False)
    parser.add_argument("-d", "--beep_duration", help="time in seconds for a beep duration", type=float, default=0.06)
    parser.add_argument("-q", "--quiet_duration", help="time in seconds between beeps", type=float, default=0.1)
    parser.add_argument("-n", "--beep_count", help="number of beeps", type=int, default=2)
    parser.add_argument("-p", "--pin", help="gpio pin (using BCM numbering)", type=int, required=True)
    parser.add_argument("-f", "--input_file", help="input file (yaml format)", default=None)
    parser.add_argument("-g", "--log_level", help="log level", type=int, default=logging.INFO)
    args = parser.parse_args()

    # logging setup
    logger = util.set_logger(level=args.log_level)

    buzzer = Buzzer(args.pin)
    buzzer.start()

    subscriber = Subscriber(args.endpoint, args.rootCA, args.key, args.cert, args.clientID, args.log_level)

    # Load configuration file
    if args.input_file is not None:
        f = open(args.input_file)
        topics = yaml.safe_load(f)
        for t in topics[args.endpoint]:
            print("Subscribing to {}".format(t))
            subscriber.subscribe(t, my_callback)
            time.sleep(2)  # pause between subscribes (maybe not needed?)

    for t in args.topic:
        subscriber.subscribe(t, my_callback)
        time.sleep(2)  # pause

    # Loop forever
    try:
        while True:
            time.sleep(0.2)  # sleep needed because CPU race
            pass
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
