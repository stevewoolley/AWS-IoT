#!/usr/bin/env python

import argparse
import logging
from cloud_tools import Publisher

LOG_FILE = '/var/log/iot.log'


def publicize(article):
    logging.info("publisher {} {}".format(args.name, article))
    # publish to thing
    Publisher(
        args.endpoint,
        args.rootCA,
        args.key,
        args.cert,
        clientID=args.clientID,
        log_level=args.log_level
    ).report(Publisher.THING_SHADOW.format(args.name), {Publisher.STATE: {Publisher.REPORTED: article}})


if __name__ == "__main__":

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
    parser.add_argument("-i", "--clientID", help="Client ID", default=None)
    parser.add_argument("-r", "--rootCA", help="Root CA file path", required=True)
    parser.add_argument("-c", "--cert", help="Certificate file path")
    parser.add_argument("-k", "--key", help="Private key file path")

    parser.add_argument("-s", "--source", help="source", default='message')
    parser.add_argument("-v", "--value", help="value", default='Foo')
    args = parser.parse_args()

    logging.basicConfig(filename=LOG_FILE, level=args.log_level)

    publicize({args.source: args.value})

