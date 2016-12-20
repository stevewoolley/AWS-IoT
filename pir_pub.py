#!/usr/bin/env python

import argparse
import time
import sys
from cloud_tools import Reporter
from pir import PIR

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", help="Thing name", required=True)
parser.add_argument("-z", "--active_sleep", help="sleep seconds during movement", type=float, default=0.5)
parser.add_argument("-y", "--passive_sleep", help="sleep seconds while quiet", type=float, default=0.5)
parser.add_argument("-p", "--pin", help="gpio pin (using BCM numbering)", type=int, required=True)
parser.add_argument("-s", "--source", help="Source", default="PIR")
parser.add_argument("-x", "--alert_count", help="number of beeps", type=int, default=1)
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
                Reporter(args.name).put(Reporter.REPORTED,
                                        {args.source: current_state, 'alert_count': args.alert_count})
            time.sleep(args.active_sleep)
        else:
            if current_state == 1:
                current_state = 0
                Reporter(args.name).put(Reporter.REPORTED, {args.source: current_state, 'alert_count': 0})
            time.sleep(args.passive_sleep)
except (KeyboardInterrupt, SystemExit):
    sys.exit()
