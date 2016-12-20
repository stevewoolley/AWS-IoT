#!/usr/bin/env python

import argparse
import time
import sys
from cloud_tools import Reporter, Publisher
from pir import PIR

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", help="Thing name", required=True)
parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint")
parser.add_argument("-r", "--rootCA", help="Root CA file path")
parser.add_argument("-c", "--cert", help="Certificate file path")
parser.add_argument("-k", "--key", help="Private key file path")
parser.add_argument("-i", "--clientID", help="Client ID", default='')
parser.add_argument("-t", "--topic", help="MQTT topic(s)", nargs='+')
parser.add_argument("-z", "--active_sleep", help="sleep seconds during movement", type=float, default=0.5)
parser.add_argument("-y", "--passive_sleep", help="sleep seconds while quiet", type=float, default=0.5)
parser.add_argument("-p", "--pin", help="gpio pin (using BCM numbering)", type=int, required=True)
parser.add_argument("-s", "--source", help="Source", default="PIR")
args = parser.parse_args()

pir = PIR(args.pin)
pir.start()

# initialize

current_state = 0
try:
    while True:
        if pir.movement():
            if current_state == 0:
                current_state = 1
                Reporter(args.name).put(Reporter.REPORTED, {args.source: current_state})
                if args.topic is not None:
                    for t in args.topic:
                        Publisher(args.endpoint, args.rootCA, args.key, args.cert).publish(t,
                                                                                           {'name': args.name,
                                                                                            args.source: current_state})
            time.sleep(args.active_sleep)
        else:
            if current_state == 1:
                current_state = 0
                Reporter(args.name).put(Reporter.REPORTED, {args.source: current_state})
                for t in args.topic:
                    Publisher(args.endpoint, args.rootCA, args.key, args.cert).publish(t,
                                                                                       {'name': args.name,
                                                                                        args.source: current_state})
            time.sleep(args.passive_sleep)
except (KeyboardInterrupt, SystemExit):
    sys.exit()
