#!/usr/bin/env python

import argparse
import logging
import platform
from cloud_tools import Publisher

LOG_FILE = '/var/log/iot.log'


def trigger(article):
    logging.info("trigger {}".format(article))
    # publish to any topics
    if args.topic is not None:
        for t in args.topic:
            Publisher(
                args.endpoint,
                args.rootCA,
                args.key,
                args.cert,
                clientID=args.clientID,
                log_level=args.log_level
            ).report(t, article)


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
    parser.add_argument("-i", "--clientID", help="Client ID", default=None)
    parser.add_argument("-r", "--rootCA", help="Root CA file path", required=True)
    parser.add_argument("-c", "--cert", help="Certificate file path")
    parser.add_argument("-k", "--key", help="Private key file path")

    parser.add_argument("-s", "--source", help="source", default="source")
    parser.add_argument("-t", "--topic", help="MQTT topic(s)", nargs='+', required=False)
    parser.add_argument("-v", "--value", help="value", default=platform.node().split('.')[0])

    parser.add_argument("-l", "--log_level", help="Log Level", default=logging.INFO)
    args = parser.parse_args()

    logging.basicConfig(filename=LOG_FILE, level=args.log_level)

    trigger({args.source: args.value})
