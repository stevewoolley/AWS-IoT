#!/usr/bin/env python

import argparse
import logging
import platform
import time
from cloud_tools import Publisher
from gpiozero import Button
from signal import pause

MESSAGE = 'message'
SOURCE = 'source'
ALERT_COUNT = 'alert_count'
LOG_FILE = '/var/log/iot.log'


def high():
    if args.cushion > 0.0:
        time.sleep(args.cushion)
        if sensor.active_time >= args.cushion:
            publicize({SOURCE: args.source,
                       MESSAGE: args.high_value,
                       ALERT_COUNT: args.high_alert})
    else:
        publicize({SOURCE: args.source,
                   MESSAGE: args.high_value,
                   ALERT_COUNT: args.high_alert})


def low():
    if args.cushion > 0.0:
        time.sleep(args.cushion)
        if sensor.active_time is None:
            publicize({SOURCE: args.source,
                       MESSAGE: args.low_value,
                       ALERT_COUNT: args.low_alert})
    else:
        publicize({SOURCE: args.source,
                   MESSAGE: args.low_value,
                   ALERT_COUNT: args.low_alert})


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
    parser.add_argument("-y", "--high_value", help="high value", default="high")
    parser.add_argument("-z", "--low_value", help="low value", default="low")
    parser.add_argument("-a", "--high_alert", help="high alert", type=int, default=2)
    parser.add_argument("-b", "--low_alert", help="low alert", type=int, default=1)
    parser.add_argument("-w", "--cushion", help="seconds of cushion for twitchy sensor", type=float, default=0.0)

    parser.add_argument("-l", "--log_level", help="Log Level", default=logging.INFO)

    args = parser.parse_args()

    logging.basicConfig(filename=LOG_FILE, level=args.log_level)

    sensor = Button(args.pin)

    sensor.when_pressed = high
    sensor.when_released = low

    pause()
