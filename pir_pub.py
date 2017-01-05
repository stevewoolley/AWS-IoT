#!/usr/bin/env python

import argparse
import time
import sys
import platform
import logging
from cloud_tools import Publisher
from pir import PIR


def publicize(article):
    logger.info("publicize {} {}".format(args.name, article))
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
    # publish to thing and any topics required
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
    parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint")
    parser.add_argument("-r", "--rootCA", help="Root CA file path")
    parser.add_argument("-c", "--cert", help="Certificate file path")
    parser.add_argument("-k", "--key", help="Private key file path")
    parser.add_argument("-i", "--clientID", help="Client ID", default='')

    parser.add_argument("-s", "--source", help="Source", default="pir")
    parser.add_argument("-n", "--name", help="Thing name", default=platform.node().split('.')[0])
    parser.add_argument("-t", "--topic", help="MQTT topic(s)", nargs='+', required=False)

    parser.add_argument("-z", "--active_sleep", help="sleep seconds during movement", type=float, default=2.0)
    parser.add_argument("-y", "--passive_sleep", help="sleep seconds while quiet", type=float, default=0.5)
    parser.add_argument("-p", "--pin", help="gpio pin (using BCM numbering)", type=int, required=True)

    parser.add_argument("-l", "--log_level", help="Log Level", default=logging.WARNING)

    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)
    logger = logging.getLogger(__name__)

    pir = PIR(args.pin)
    pir.start()

    current_state = 0
    try:
        while True:
            sleep = 0
            if pir.movement():
                if current_state == 0:
                    current_state = 1
                    publicize({args.source: current_state})
                sleep = args.active_sleep
            else:
                if current_state == 1:
                    current_state = 0
                    publicize({args.source: current_state})
                sleep = args.passive_sleep
            # let's rest
            time.sleep(sleep)
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
