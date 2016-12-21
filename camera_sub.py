#!/usr/bin/env python

import argparse
import time
import sys
import json
import util
from cloud_tools import Subscriber, Reporter
from camera import Camera


def my_callback(client, userdata, message):
    msg = json.loads(message.payload)
    if camera.snapping:
        Reporter(args.name).put(Reporter.REPORTED, {'camera': False})
        camera.stop_snapping()
    else:
        Reporter(args.name).put(Reporter.REPORTED, {'camera': True})
        camera.start_snapping()


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
    parser.add_argument("-w", "--sleep", help="sleep seconds between snapshots", type=float, default=3.0)
    parser.add_argument("-s", "--source", help="Source", required=True)
    parser.add_argument("-f", "--image_format", help="Image Format(jpg, png, etc.)", default='png')
    parser.add_argument("-b", "--bucket", help="S3 snapshot bucket", default=None)
    args = parser.parse_args()

    camera = Camera(
        base_filename=args.source,
        rotation=args.rotation,
        horizontal_resolution=args.horizontal_resolution,
        vertical_resolution=args.vertical_resolution
    )
    camera.start()

    subscriber = Subscriber(args.endpoint, args.rootCA, args.key, args.cert, args.clientID)

    for t in args.topic:
        subscriber.subscribe(t, my_callback)
        time.sleep(2)  # pause

    # Loop forever
    last_filename = None
    try:
        while True:
            if args.bucket is not None:
                if camera.filename != last_filename:
                    # copy to web image bucket
                    util.copy_to_s3(camera.filename, args.bucket, "{}.{}".format(args.source, args.image_format))
                    last_filename = camera.filename
                    time.sleep(args.sleep)
            time.sleep(0.2)  # sleep needed because CPU race
            pass
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
