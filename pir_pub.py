#!/usr/bin/env python

import argparse
import time
import sys
import platform
import logging
from cloud_tools import Publisher
from pir import PIR

TOPIC = "$aws/things/{}/shadow/update"

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint")
parser.add_argument("-r", "--rootCA", help="Root CA file path")
parser.add_argument("-c", "--cert", help="Certificate file path")
parser.add_argument("-k", "--key", help="Private key file path")
parser.add_argument("-i", "--clientID", help="Client ID", default='')

parser.add_argument("-s", "--source", help="Source", default="PIR")
parser.add_argument("-n", "--name", help="Thing name", default=platform.node().split('.')[0])
parser.add_argument("-t", "--topic", help="MQTT topic(s)", nargs='+', required=False)

parser.add_argument("-z", "--active_sleep", help="sleep seconds during movement", type=float, default=0.5)
parser.add_argument("-y", "--passive_sleep", help="sleep seconds while quiet", type=float, default=0.5)
parser.add_argument("-p", "--pin", help="gpio pin (using BCM numbering)", type=int, required=True)

parser.add_argument("-l", "--log_level", help="Log Level", default=logging.WARNING)

args = parser.parse_args()

logging.basicConfig(level=args.log_level)
logger = logging.getLogger(__name__)

pir = PIR(args.pin)
pir.start()

# initialize

current_state = 0
try:
    while True:
        there_is_a_change = False
        sleep = 0
        if pir.movement():
            if current_state == 0:
                current_state = 1
                there_is_a_change = True
                logger.info("pir_pub {} {}".format(args.name, current_state))
            sleep = args.active_sleep
        else:
            if current_state == 1:
                current_state = 0
                there_is_a_change = True
                logger.info("pir_pub {} {}".format(args.name, current_state))
            sleep = args.passive_sleep
        #
        if there_is_a_change:
            Publisher(
                args.endpoint,
                args.rootCA,
                args.key,
                args.cert,
                clientID=args.clientID,
                log_level=args.log_level
            ).report(TOPIC.format(args.name), {args.source: current_state})
            # publish to any additional topics
            if args.topic is not None:
                for t in args.topic:
                    Publisher(
                        args.endpoint,
                        args.rootCA,
                        args.key,
                        args.cert,
                        clientID=args.clientID,
                        log_level=args.log_level
                    ).report(t, {args.source: current_state})
        # let's rest
        time.sleep(sleep)
except (KeyboardInterrupt, SystemExit):
    sys.exit()
