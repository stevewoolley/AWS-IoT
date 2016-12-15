#!/usr/bin/env python
import argparse
import time
import util
import json
import logging
import sys
from thing import Thing
from pir import PIR

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", help="Thing name", required=True)
parser.add_argument("-g", "--log_level", help="log level", type=int, default=logging.WARNING)
parser.add_argument("-n", "--alert_count", help="number of beeps", type=int, default=2)
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
