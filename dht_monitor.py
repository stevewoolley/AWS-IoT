#!/usr/bin/env python
import argparse
import logging
import json
import time
import Adafruit_DHT
from publisher import Publisher

# Define sensor type constants.
DHT11 = 11
DHT22 = 22
AM2302 = 22
SENSORS = [DHT11, DHT22, AM2302]


def read_retry(sensor, pin, retries=15, delay_seconds=2):
    if sensor not in SENSORS:
        raise ValueError('Expected DHT11, DHT22, or AM2302 sensor value.')
    for i in range(retries):
        h, t = Adafruit_DHT.read(sensor, pin)
        if h is not None and t is not None:
            return h, t
        time.sleep(delay_seconds)
    return None, None


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
parser.add_argument("-y", "--dht_type", help="DHT sensor type %s" % SENSORS, type=int, default=DHT22)
parser.add_argument("-g", "--log_level", help="log level", type=int, default=logging.INFO)
args = parser.parse_args()

humidity, temperature = read_retry(args.dht_type, args.pin)

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
    print "ERROR: publish {} {}".format(args.topic, ex.message)
