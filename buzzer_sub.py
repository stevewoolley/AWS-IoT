#!/usr/bin/env python

import argparse
from gpiozero import Buzzer
import time
import sys
import json
import yaml
import logging
from cloud_tools import Subscriber

LEVEL = 'level'
ALERT_COUNT = 'alert_count'
OFF = 'off'
LOG_FILE = '/var/log/iot.log'


def my_callback(client, userdata, message):
    logging.info("buzzer_sub {} {} {}".format(message.topic, message.qos, message.payload))
    msg = json.loads(message.payload)
    # handle based on message
    if LEVEL in msg:
        if msg[LEVEL] == logging.CRITICAL:
            buzzer.on()
        elif msg[LEVEL] == logging.ERROR:
            buzzer.beep(1, 1)
        elif msg[LEVEL] == logging.INFO:  # default
            buzzer.beep(args.on_time, args.off_time, args.beeps)
        elif msg[LEVEL] == logging.NOTSET:
            buzzer.off()
        else:
            buzzer.beep(args.on_time, args.off_time, msg[ALERT_COUNT])
    elif ALERT_COUNT in msg:
        buzzer.beep(args.on_time, args.off_time, msg[ALERT_COUNT])
    elif OFF in msg:
        buzzer.off()
    else:
        buzzer.beep(args.on_time, args.off_time, args.beeps)


if __name__ == "__main__":

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
    parser.add_argument("-i", "--clientID", help="Client ID", default='')
    parser.add_argument("-r", "--rootCA", help="Root CA file path", required=True)
    parser.add_argument("-c", "--cert", help="Certificate file path")
    parser.add_argument("-k", "--key", help="Private key file path")

    parser.add_argument("-p", "--pin", help="gpio pin (using BCM numbering)", type=int, required=True)
    parser.add_argument("-n", "--beeps", help="Default number of times to beep", type=int, default=2)
    parser.add_argument("-x", "--on_time", help="Default number of seconds on", type=float, default=0.06)
    parser.add_argument("-y", "--off_time", help="Default number of seconds off", type=float, default=0.1)
    parser.add_argument("-m", "--mode", help="Default mode: 1=flash 2=toggle ", type=int, default=1)

    parser.add_argument("-t", "--topic", help="MQTT topic(s)", nargs='+', required=False)
    parser.add_argument("-f", "--input_file", help="input file (yaml format)", default=None)

    parser.add_argument("-l", "--log_level", help="Log Level", default=logging.INFO)

    args = parser.parse_args()

    logging.basicConfig(filename=LOG_FILE, level=args.log_level)

    buzzer = Buzzer(args.pin)

    subscriber = Subscriber(args.endpoint, args.rootCA, args.key, args.cert, args.clientID)

    # Load configuration file
    if args.input_file is not None:
        f = open(args.input_file)
        topics = yaml.safe_load(f)
        for t in topics[args.endpoint]:
            logging.info("Subscribing to {}".format(t))
            subscriber.subscribe(t, my_callback)
            time.sleep(2)  # pause between subscribes (maybe not needed?)

    for t in args.topic:
        logging.info("Subscribing to {}".format(t))
        subscriber.subscribe(t, my_callback)
        time.sleep(2)  # pause

    # Loop forever
    try:
        while True:
            time.sleep(0.2)  # sleep needed because CPU race
            pass
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
