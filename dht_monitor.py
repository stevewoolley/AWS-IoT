#!/usr/bin/env python

import argparse
import time
import Adafruit_DHT
import logging
import platform
from cloud_tools import Publisher

# Define sensor type constants.
DHT11 = 11
DHT22 = 22
AM2302 = 22
SENSORS = [DHT11, DHT22, AM2302]
THING_SHADOW = "$aws/things/{}/shadow/update"


def read_retry(sensor, pin, retries=15, delay_seconds=2):
    if sensor not in SENSORS:
        raise ValueError('Expected DHT11, DHT22, or AM2302 sensor value.')
    for i in range(retries):
        h, t = Adafruit_DHT.read(sensor, pin)
        if h is not None and t is not None:
            return h, t
        time.sleep(delay_seconds)
    return None, None


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()

    parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
    parser.add_argument("-r", "--rootCA", help="Root CA file path", required=True)
    parser.add_argument("-c", "--cert", help="Certificate file path", required=True)
    parser.add_argument("-k", "--key", help="Private key file path", required=True)
    parser.add_argument("-i", "--clientID", help="Client ID", default=None)

    parser.add_argument("-s", "--source", help="Source", default=platform.node().split('.')[0])
    parser.add_argument("-p", "--pin", help="gpio pin (using BCM numbering)", type=int, required=True)
    parser.add_argument("-y", "--dht_type", help="DHT sensor type %s" % SENSORS, type=int, default=DHT22)

    parser.add_argument("-l", "--log_level", help="Log Level", default=logging.WARNING)

    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)
    logger = logging.getLogger(__name__)

    humidity, temperature = read_retry(args.dht_type, args.pin)
    logger.info("dht_monitor {} humidity {} temperature {}".format(args.source, humidity, temperature))

    Publisher(
        args.endpoint,
        args.rootCA,
        args.key,
        args.cert,
        clientID=args.clientID,
        log_level=args.log_level
    ).report(THING_SHADOW.format(args.source), {"temperature": temperature, "humidity": humidity})
