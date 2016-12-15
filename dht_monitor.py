#!/usr/bin/env python
import argparse
import logging
import time
import util
import Adafruit_DHT
from thing import Thing

# Define sensor type constants.
DHT11 = 11
DHT22 = 22
AM2302 = 22
SENSORS = [DHT11, DHT22, AM2302]
REPORTED = 'reported'


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
parser.add_argument("-n", "--name", help="Thing name", required=True)
parser.add_argument("-g", "--log_level", help="log level", type=int, default=logging.WARNING)
args = parser.parse_args()

# logging setup
logger = util.set_logger(level=args.log_level)

humidity, temperature = read_retry(args.dht_type, args.pin)
thing = Thing(args.name, args.log_level)
thing.put(REPORTED, {"temperature": temperature, "humidity": humidity})
