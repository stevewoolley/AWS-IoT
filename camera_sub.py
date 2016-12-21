#!/usr/bin/env python

import argparse
import time
import sys
import json
import util
import datetime
import os
from cloud_tools import Subscriber, Reporter
from camera import Camera

STORAGE_DIRECTORY = '/tmp'
SNAP_FILENAME = 'snapshot.png'
DATE_FORMAT = '%Y_%m_%d_%H_%M_%S'


def my_callback(client, userdata, message):
    msg = json.loads(message.payload)
    print >> sys.stderr, 'callback {}'.format(msg)
    if camera.snap('/'.join((STORAGE_DIRECTORY, SNAP_FILENAME))):
        filename, file_extension = os.path.splitext(SNAP_FILENAME)
        f = "{}_{}{}".format(datetime.datetime.now().strftime(DATE_FORMAT), args.source, file_extension)
        print >> sys.stderr, 'callback new file'.format(f)
        Reporter(args.name).put(Reporter.REPORTED, {'last_snapshot': f})
        util.copy_to_s3(camera.filename, args.bucket, f)


if __name__ == "__main__":

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", help="pi AWS thing name", required=True)
    parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
    parser.add_argument("-r", "--rootCA", help="Root CA file path", required=True)
    parser.add_argument("-c", "--cert", help="Certificate file path")
    parser.add_argument("-k", "--key", help="Private key file path")
    parser.add_argument("-i", "--clientID", help="Client ID", default='')
    parser.add_argument("-t", "--topic", help="MQTT topic(s)", nargs='+', required=True)
    parser.add_argument("-x", "--horizontal_resolution", help="horizontal_resolution", type=int, default=640)
    parser.add_argument("-y", "--vertical_resolution", help="vertical resolution", type=int, default=480)
    parser.add_argument("-z", "--rotation", help="image rotation", type=int, default=0)
    parser.add_argument("-s", "--source", help="Source", required=True)
    parser.add_argument("-b", "--bucket", help="S3 snapshot bucket", default=None)
    args = parser.parse_args()
    print >> sys.stderr, 'debug 1'

    camera = Camera(rotation=args.rotation, horizontal_resolution=args.horizontal_resolution,
                    vertical_resolution=args.vertical_resolution)
    print >> sys.stderr, 'debug 2'

    subscriber = Subscriber(args.endpoint, args.rootCA, args.key, args.cert, args.clientID)
    print >> sys.stderr, 'debug 3'

    for t in args.topic:
        print >> sys.stderr, 'subscribing {}'.format(t)
        subscriber.subscribe(t, my_callback)
        time.sleep(2)  # pause

    # Loop forever
    try:
        while True:
            time.sleep(0.2)  # sleep needed because CPU race
            pass
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
