#!/usr/bin/env python

import argparse
import time
import sys
import logging
import platform
from cloud_tools import Publisher
from sensor import Sensor

MESSAGE = 'message'
SOURCE = 'source'
ALERT_COUNT = 'alert_count'
LOG_FILE = '/var/log/iot.log'


def publicize(article):
    logging.info("sensor_pub {} {}".format(args.name, article))
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
    doc = {args.source: article[MESSAGE]}
    Publisher(
        args.endpoint,
        args.rootCA,
        args.key,
        args.cert,
        clientID=args.clientID,
        log_level=args.log_level
    ).report(Publisher.THING_SHADOW.format(args.name), {Publisher.STATE: {Publisher.REPORTED: doc}})


if __name__ == "__main__":

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint")
    parser.add_argument("-i", "--clientID", help="Client ID", default='')
    parser.add_argument("-r", "--rootCA", help="Root CA file path")
    parser.add_argument("-c", "--cert", help="Certificate file path")
    parser.add_argument("-k", "--key", help="Private key file path")

    parser.add_argument("-s", "--source", help="Source", default="Sensor")
    parser.add_argument("-n", "--name", help="Thing name", default=platform.node().split('.')[0])
    parser.add_argument("-t", "--topic", help="MQTT topic(s)", nargs='+', required=False)

    parser.add_argument("-p", "--pin", help="gpio pin (BCM)", type=int, required=True)
    parser.add_argument("-y", "--high_value", help="high value", default=Sensor.HIGH)
    parser.add_argument("-z", "--low_value", help="low value", default=Sensor.LOW)

    parser.add_argument("-l", "--log_level", help="Log Level", default=logging.INFO)

    args = parser.parse_args()

    logging.basicConfig(filename=LOG_FILE, level=args.log_level)

    sensor = Sensor(args.pin)
    sensor.start()

    last_state = None
    current_state = None
    try:
        while True:
            status = None
            current_state = sensor.reading()
            if current_state != last_state:
                alert_count = 2
                last_state = current_state  # reset state value
                if current_state == Sensor.LOW:
                    alert_count = 1
                    status = args.low_value
                else:
                    status = args.high_value
                # publish change to thing
                publicize({SOURCE: args.source,
                           MESSAGE: status,
                           ALERT_COUNT: alert_count})
            time.sleep(0.2)
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
