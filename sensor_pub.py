#!/usr/bin/env python

import argparse
import time
import util
import json
import logging
from publisher import Publisher
from sensor import Sensor

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
parser.add_argument("-r", "--rootCA", help="Root CA file path", required=True)
parser.add_argument("-c", "--cert", help="Certificate file path")
parser.add_argument("-k", "--key", help="Private key file path")
parser.add_argument("-t", "--topic", help="MQTT topic", required=True)
parser.add_argument("-s", "--source", help="Source")
parser.add_argument("-p", "--pin", help="gpio pin (BCM)", type=int, required=True)
parser.add_argument("-y", "--high_value", help="high value", default=Sensor.HIGH)
parser.add_argument("-z", "--low_value", help="low value", default=Sensor.LOW)
parser.add_argument("-g", "--log_level", help="logging level", type=int, default=logging.INFO)
args = parser.parse_args()

# logging setup
logger = util.set_logger(level=args.log_level)

sensor = Sensor(args.pin)
sensor.start()

last_state = None
status = None
while True:
    current_state = sensor.reading()
    if current_state != last_state:
        last_state = current_state  # reset state value
        if current_state == Sensor.LOW:
            status = args.low_value
        else:
            status = args.high_value
        logger.debug("sensor-monitor: changed %s %s" % (args.topic_key, str(status)))

        # publish
        data = dict()
        if args.source is None:
            data["source"] = args.topic
        else:
            data["source"] = args.source
        data["message"] = status
        msg = json.dumps(data)

        try:
            Publisher(
                args.endpoint,
                args.rootCA,
                args.key,
                args.cert
            ).publish(args.topic, msg)
        except Exception as ex:
            print "ERROR: publish %s %s" % (args.topic, ex.message)

    time.sleep(0.2)
