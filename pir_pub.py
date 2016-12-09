#!/usr/bin/env python
import argparse
import time
import util
import json
import logging
import sys
from publisher import Publisher
from pir import PIR

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
parser.add_argument("-r", "--rootCA", help="Root CA file path", required=True)
parser.add_argument("-c", "--cert", help="Certificate file path", required=True)
parser.add_argument("-k", "--key", help="Private key file path", required=True)
parser.add_argument("-t", "--topic", help="MQTT topic(s)", nargs='+', required=True)
parser.add_argument("-s", "--source", help="Source", required=True)
parser.add_argument("-p", "--pin", help="gpio pin (BCM)", type=int, required=True)
parser.add_argument("-n", "--alert_count", help="number of alerts", type=int, default=0)
parser.add_argument("-x", "--active_sleep", help="sleep seconds during movement", type=float, default=5.0)
parser.add_argument("-y", "--passive_sleep", help="sleep seconds while quiet", type=float, default=0.5)
parser.add_argument("-g", "--log_level", help="logging level", type=int, default=logging.INFO)
args = parser.parse_args()

# logging setup
logger = util.set_logger(level=args.log_level)

pir = PIR(args.pin)
pir.start()

# initialize
data = {'state': {'reported': {}}}

try:
    while True:
        if pir.movement():
            data["state"]["reported"][args.source] = 1
            data["alert_count"] = args.alert_count
            msg = json.dumps(data)
            obj = []
            for t in args.topic:
                obj.append({'topic': t, 'payload': msg})
            try:
                Publisher(
                    args.endpoint,
                    args.rootCA,
                    args.key,
                    args.cert
                ).publish_multiple(obj)
            except Exception as ex:
                logger.error("ERROR publish {}".format(ex.message))
            time.sleep(args.active_sleep)
        else:
            time.sleep(args.passive_sleep)
except (KeyboardInterrupt, SystemExit):
    sys.exit()
