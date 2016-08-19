#!/usr/bin/env python

import argparse
import time
import util
import json
import logging
import sys
from publisher import Publisher
from sensor import Sensor

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
parser.add_argument("-r", "--rootCA", help="Root CA file path", required=True)
parser.add_argument("-c", "--cert", help="Certificate file path")
parser.add_argument("-k", "--key", help="Private key file path")
parser.add_argument("-t", "--topic", help="MQTT topic", required=True)
parser.add_argument("-o", "--topic2", help="Additional IoT topic")
parser.add_argument("-x", "--topic3", help="Additional IoT topic")
parser.add_argument("-s", "--source", help="Source", required=True)
parser.add_argument("-p", "--pin", help="gpio pin (BCM)", type=int, required=True)
parser.add_argument("-y", "--high_value", help="high value", default=Sensor.HIGH)
parser.add_argument("-z", "--low_value", help="low value", default=Sensor.LOW)
parser.add_argument("-g", "--log_level", help="logging level", type=int, default=logging.INFO)
args = parser.parse_args()

# logging setup
logger = util.set_logger(level=args.log_level)

sensor = Sensor(args.pin, args.source)
sensor.start()

# Lookup data structure
data = dict()
data["state"] = {}
data["state"]["reported"] = {}

last_state = None
status = None

try:
    while True:
        current_state = sensor.reading()
        if current_state != last_state:
            last_state = current_state  # reset state value
            if current_state == Sensor.LOW:
                status = args.low_value
            else:
                status = args.high_value
            data["state"]["reported"][args.source] = str(status)
            msg = json.dumps(data)
            obj = []
            if args.topic is not None:
                obj.append({'topic': args.topic, 'payload': msg})
            if args.topic2 is not None:
                obj.append({'topic': args.topic2, 'payload': msg})
            if args.topic3 is not None:
                obj.append({'topic': args.topic3, 'payload': msg})
            try:
                logger.info("sensor_pub %s" % obj)
                Publisher(
                    args.endpoint,
                    args.rootCA,
                    args.key,
                    args.cert
                ).publish_multiple(obj)
            except Exception as ex:
                logger.error("ERROR publish %s" % ex.message)
        time.sleep(0.2)
except (KeyboardInterrupt, SystemExit):
    sys.exit()
