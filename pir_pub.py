#!/usr/bin/env python

import argparse
import time
import sys
import logging
import platform
from cloud_tools import Publisher
from gpiozero import MotionSensor

LOG_FILE = '/var/log/iot.log'


def publicize(article):
    logging.info("publicize pir {} {}".format(args.name, article))
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

    parser.add_argument("-s", "--source", help="Source", required=True)
    parser.add_argument("-n", "--name", help="Thing name", default=platform.node().split('.')[0])
    parser.add_argument("-t", "--topic", help="MQTT topic(s)", nargs='+', required=False)

    parser.add_argument("-p", "--pin", help="gpio pin (using BCM numbering)", type=int, required=True)
    parser.add_argument("-l", "--log_level", help="Log Level", default=logging.INFO)
    args = parser.parse_args()

    logging.basicConfig(filename=LOG_FILE, level=args.log_level)

    pir = MotionSensor(args.pin)

    try:
        motion = False
        while True:
            if motion is False and pir.motion_detected:
                motion = True
                publicize({args.source: motion})
            elif motion is True and not pir.motion_detected:
                motion = False
                publicize({args.source: motion})
            time.sleep(0.2)
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
