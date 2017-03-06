#!/usr/bin/env python

import argparse
import util
import datetime
import yaml
import logging
import time
import sys
import subprocess
from cloud_tools import Subscriber

STORAGE_DIRECTORY = '/tmp'
IMAGE_FILE_EXT = 'jpg'
DATE_FORMAT = '%Y-%m-%d-%H-%M-%S'
LOG_FILE = '/var/log/iot.log'


def my_callback(mqttc, obj, msg):
    logging.info("camera_sub {} {} {}".format(msg.topic, msg.qos, msg.payload))
    try:
        local_filename = "{}.{}".format(args.source, IMAGE_FILE_EXT)
        remote_filename = "{}_{}.{}".format(args.source, datetime.datetime.now().strftime(DATE_FORMAT), IMAGE_FILE_EXT)
        filename = '/'.join((STORAGE_DIRECTORY, remote_filename))
        raspistill = ['/usr/bin/raspistill',
                      '-w', str(args.horizontal_resolution),
                      '-h', str(args.vertical_resolution),
                      '-rot', str(args.rotation),
                      '-a', util.now_string(),
                      '-o', filename
                      ]
        subprocess.check_call(raspistill)
        util.copy_to_s3(filename, args.bucket, local_filename)
    except:
        logging.error("camera_sub {}".format(sys.exc_info()[0]))


if __name__ == "__main__":

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
    parser.add_argument("-r", "--rootCA", help="Root CA file path", required=True)
    parser.add_argument("-c", "--cert", help="Certificate file path")
    parser.add_argument("-k", "--key", help="Private key file path")
    parser.add_argument("-i", "--clientID", help="Client ID", default='')

    parser.add_argument("-x", "--horizontal_resolution", help="horizontal_resolution", type=int, default=640)
    parser.add_argument("-y", "--vertical_resolution", help="vertical resolution", type=int, default=480)
    parser.add_argument("-z", "--rotation", help="image rotation", type=int, default=0)

    parser.add_argument("-s", "--source", help="Source", required=True)
    parser.add_argument("-b", "--bucket", help="S3 snapshot bucket", default=None)

    parser.add_argument("-t", "--topic", help="MQTT topic(s)", nargs='+', required=True)
    parser.add_argument("-f", "--input_file", help="input file (yaml format)", default=None)

    parser.add_argument("-l", "--log_level", help="Log Level", default=logging.WARNING)

    args = parser.parse_args()

    logging.basicConfig(filename=LOG_FILE, level=args.log_level)

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
