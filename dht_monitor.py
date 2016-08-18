#!/usr/bin/env python

import argparse
import logging
import json
import Adafruit_DHT
from publisher import Publisher

SENSOR_ARGS = {11: Adafruit_DHT.DHT11,
               22: Adafruit_DHT.DHT22,
               2302: Adafruit_DHT.AM2302}

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
parser.add_argument("-r", "--rootCA", help="Root CA file path", required=True)
parser.add_argument("-c", "--cert", help="Certificate file path")
parser.add_argument("-k", "--key", help="Private key file path")
parser.add_argument("-i", "--clientID", help="Client ID", default='')  # empty string auto generates unique client ID
parser.add_argument("-t", "--topic", help="IoT topic", required=True)
parser.add_argument("-o", "--topic2", help="Additional IoT topic")
parser.add_argument("-p", "--pin", help="gpio pin (using BCM numbering)", type=int, required=True)
parser.add_argument("-y", "--dht_type", help="DHT sensor type %s" % (str(SENSOR_ARGS.keys())), type=int,
                    default=Adafruit_DHT.DHT22)
parser.add_argument("-g", "--log_level", help="log level", type=int, default=logging.INFO)
args = parser.parse_args()

humidity, temperature = Adafruit_DHT.read(SENSOR_ARGS[args.dht_type], args.pin)

# Lookup system_info
data = dict()
data["state"] = {}
data["state"]["reported"] = {}
data["state"]["reported"]["temperature"] = temperature
data["state"]["reported"]["humidity"] = humidity

msg = json.dumps(data)
# Publish

try:
    if args.topic2 is None:
        Publisher(
            args.endpoint,
            args.rootCA,
            args.key,
            args.cert
        ).publish(args.topic, msg)
    else:
        Publisher(
            args.endpoint,
            args.rootCA,
            args.key,
            args.cert
        ).publish_multiple([{'topic': args.topic, 'payload': msg}, {'topic': args.topic2, 'payload': msg}])
except Exception as ex:
    print "ERROR: publish %s %s" % (args.topic, ex.message)
