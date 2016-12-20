#!/usr/bin/env python
import argparse
import time
import sys
from cloud_tools import Reporter, Publisher
from sensor import Sensor

REPORTED = 'reported'

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", help="Thing name", required=True)
parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint")
parser.add_argument("-i", "--clientID", help="Client ID", default='')
parser.add_argument("-r", "--rootCA", help="Root CA file path")
parser.add_argument("-c", "--cert", help="Certificate file path")
parser.add_argument("-k", "--key", help="Private key file path")
parser.add_argument("-t", "--topic", help="MQTT topic(s)", nargs='+', required=False)
parser.add_argument("-s", "--source", help="Source", required=True)
parser.add_argument("-p", "--pin", help="gpio pin (BCM)", type=int, required=True)
parser.add_argument("-y", "--high_value", help="high value", default=Sensor.HIGH)
parser.add_argument("-z", "--low_value", help="low value", default=Sensor.LOW)
parser.add_argument("-x", "--alert_count", help="number of alerts", type=int, default=2)
args = parser.parse_args()

sensor = Sensor(args.pin)
sensor.start()

# initialize
last_state = None
reporter = Reporter(args.name)

try:
    while True:
        status = None
        current_state = sensor.reading()
        if current_state != last_state:
            last_state = current_state  # reset state value
            if current_state == Sensor.LOW:
                status = args.low_value
            else:
                status = args.high_value
            reporter.put(REPORTED, {args.source: status})
            if args.topic is not None:
                for t in args.topic:
                    Publisher(args.endpoint, args.rootCA, args.key, args.cert).publish(t, {args.source: status,
                                                                                       'alert_count': args.alert_count})
        time.sleep(0.2)
except (KeyboardInterrupt, SystemExit):
    sys.exit()
