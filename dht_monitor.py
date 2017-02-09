#!/usr/bin/env python

import argparse
import Adafruit_DHT
import logging
import platform
from cloud_tools import Publisher

# Define sensor type constants.
DHT11 = 11
DHT22 = 22
AM2302 = 22
SENSORS = [DHT11, DHT22, AM2302]
LOG_FILE = '/var/log/iot.log'


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
    parser.add_argument("-y", "--dht_type", help="DHT sensor type %s" % SENSORS, type=int, default=Adafruit_DHT.DHT22)

    parser.add_argument("-l", "--log_level", help="Log Level", default=logging.WARNING)

    args = parser.parse_args()

    logging.basicConfig(filename=LOG_FILE, level=args.log_level)

    humidity, temperature = Adafruit_DHT.read_retry(args.dht_type, args.pin)
    logging.info("dht_monitor {} humidity {} temperature {}".format(args.source, humidity, temperature))

    if humidity is not None and temperature is not None:
        Publisher(
            args.endpoint,
            args.rootCA,
            args.key,
            args.cert,
            clientID=args.clientID,
            log_level=args.log_level
        ).report(Publisher.THING_SHADOW.format(args.source),
                 {Publisher.STATE: {Publisher.REPORTED: {"temperature": temperature, "humidity": humidity}}})
