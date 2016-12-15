#!/usr/bin/env python
import argparse
import time
import Adafruit_DHT
from cloud_tools import Reporter

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
parser.add_argument("-n", "--name", help="Thing name", required=True)
parser.add_argument("-p", "--pin", help="gpio pin (using BCM numbering)", type=int, required=True)
parser.add_argument("-y", "--dht_type", help="DHT sensor type %s" % SENSORS, type=int, default=DHT22)
args = parser.parse_args()

humidity, temperature = read_retry(args.dht_type, args.pin)
Reporter(args.name).put(Reporter.REPORTED, {"temperature": temperature, "humidity": humidity})
