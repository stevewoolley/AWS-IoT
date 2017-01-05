#!/usr/bin/env python

import argparse
import time
import sys
from cloud_tools import Subscriber
import yaml
import json
import logging
from pync import Notifier

TOPICS = 'topics'
TITLE = 'title'
MESSAGE = 'message'


def my_callback(client, userdata, message):
    msg = json.loads(message.payload)
    logger.error("notifier_sub {} {} {} {}".format(message.topic, message.qos, message.payload, msg))
    logger.error("{}".format(config[TOPICS][message.topic]))
    title = message.topic
    if TITLE in config[TOPICS][message.topic]:
        title = config[TOPICS][message.topic][TITLE]
    if MESSAGE in config[TOPICS][message.topic]:
        msg = config[TOPICS][message.topic][MESSAGE]
    Notifier.notify(msg, title=title)


if __name__ == "__main__":

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
    parser.add_argument("-i", "--clientID", help="Client ID", default='')
    parser.add_argument("-r", "--rootCA", help="Root CA file path", required=True)
    parser.add_argument("-c", "--cert", help="Certificate file path")
    parser.add_argument("-k", "--key", help="Private key file path")

    parser.add_argument("-f", "--input_file", help="input file (yaml format)", default=None)

    parser.add_argument("-l", "--log_level", help="Log Level", default=logging.WARNING)

    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)
    logger = logging.getLogger(__name__)

    subscriber = Subscriber(args.endpoint, args.rootCA, args.key, args.cert, args.clientID)

    # instantiate
    config = None

    # Load configuration file
    if args.input_file is not None:
        f = open(args.input_file)
        config = yaml.safe_load(f)
        for t in config[TOPICS]:
            logger.info("Subscribing to {}".format(t))
            subscriber.subscribe(t, my_callback)
            time.sleep(2)  # pause between subscribes (maybe not needed?)

    # Loop forever
    try:
        while True:
            time.sleep(0.2)  # sleep needed because CPU race
            pass
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
