#!/usr/bin/env python

import argparse
import sys
import logging
import platform
from cloud_tools import Publisher
from gpiozero import MotionSensor

LOG_FILE = '/var/log/iot.log'
VALUE = 'value'
SOURCE = 'source'


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
    # publish to thing
    Publisher(
        args.endpoint,
        args.rootCA,
        args.key,
        args.cert,
        clientID=args.clientID,
        log_level=args.log_level
    ).report(Publisher.THING_SHADOW.format(args.name),
             {Publisher.STATE: {Publisher.REPORTED: {article[SOURCE]: article[VALUE]}}})


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
    parser.add_argument("-q", "--queue_len",
                        help="The length of the queue used to store values read from the sensor. (1 = disabled)",
                        type=int, default=1)
    parser.add_argument("-x", "--sample_rate",
                        help="The number of values to read from the device (and append to the internal queue) per second",
                        type=float, default=100)
    parser.add_argument("-y", "--threshold",
                        help="When the mean of all values in the internal queue rises above this value, the sensor will be considered active by the is_active property, and all appropriate events will be fired",
                        type=float, default=0.5)
    parser.add_argument("-l", "--log_level", help="Log Level", default=logging.INFO)
    args = parser.parse_args()

    logging.basicConfig(filename=LOG_FILE, level=args.log_level)

    pir = MotionSensor(
        args.pin,
        queue_len=args.queue_len,
        sample_rate=args.sample_rate,
        threshold=args.threshold
    )

    try:
        while True:
            pir.wait_for_motion()
            publicize({SOURCE: args.source, VALUE: True})
            pir.wait_for_no_motion()
            publicize({SOURCE: args.source, VALUE: False})
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
