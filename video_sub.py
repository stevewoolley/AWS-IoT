#!/usr/bin/env python

import argparse
import logging
import util
import time
import sys
import json
from subscriber import Subscriber
from video import Video

RECORDING = 'recording'
SNAPSHOT = 'snapshot'


def my_callback(client, userdata, message):
    msg = json.loads(message.payload)
    filename = None
    if msg.has_key(RECORDING):
        if msg[RECORDING]:
            video.start_recording()
        else:
            filename = video.stop_recording()
    if msg.has_key(SNAPSHOT):
        filename = video.snapshot()
        if args.bucket is not None:
            util.move_to_s3(filename, args.bucket, args.folder, args.name + '.png')
    if filename is not None:
        logger.info("video_sub file %s" % filename)


# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
parser.add_argument("-r", "--rootCA", help="Root CA file path", required=True)
parser.add_argument("-c", "--cert", help="Certificate file path")
parser.add_argument("-k", "--key", help="Private key file path")
parser.add_argument("-t", "--topic", help="MQTT topic(s)", nargs='+', required=True)
parser.add_argument("-x", "--horizontal_resolution", help="horizontal_resolution", type=int, default=640)
parser.add_argument("-y", "--vertical_resolution", help="vertical resolution", type=int, default=480)
parser.add_argument("-b", "--bucket", help="S3 bucket", default=None)
parser.add_argument("-f", "--folder", help="Snapshot folder", default='snapshots')
parser.add_argument("-n", "--name", help="Name", default='snapshot')
parser.add_argument("-z", "--rotation", help="image rotation", type=int, default=0)
parser.add_argument("-g", "--log_level", help="log level", type=int, default=logging.INFO)
args = parser.parse_args()

# logging setup
logger = util.set_logger(level=args.log_level)

video = Video(
    rotation=args.rotation,
    horizontal_resolution=args.horizontal_resolution,
    vertical_resolution=args.vertical_resolution
)
video.start()

subscriber = Subscriber(
    args.endpoint,
    args.rootCA,
    args.key,
    args.cert
)

for t in args.topic:
    subscriber.subscribe(t, my_callback)
    time.sleep(2)  # pause

# Loop forever
try:
    while True:
        time.sleep(0.2)  # sleep needed because CPU race
        pass
except (KeyboardInterrupt, SystemExit):
    sys.exit()
