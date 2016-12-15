#!/usr/bin/env python

import argparse
import util
import time
import sys
import json
from cloud_tools import Subscriber
from video import Video
from s3archiver import S3Archiver


def snapshot_callback(client, userdata, message):
    msg = json.loads(message.payload)
    filename = video.snapshot(annotate_text=util.now_string())
    if args.bucket is not None:
        util.copy_to_s3(filename, args.bucket, util.file_name('png', args.name))
    if args.archive_bucket is not None:
        archiver.add_file(filename)


def recording_callback(client, userdata, message):
    msg = json.loads(message.payload)
    filename = None
    if video.recording:
        filename = video.stop_recording()
    else:
        video.start_recording()
        if video.filename is not None:
            archiver.add_file(video.filename)


if __name__ == "__main__":

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
    parser.add_argument("-r", "--rootCA", help="Root CA file path", required=True)
    parser.add_argument("-c", "--cert", help="Certificate file path")
    parser.add_argument("-k", "--key", help="Private key file path")
    parser.add_argument("-x", "--horizontal_resolution", help="horizontal_resolution", type=int, default=640)
    parser.add_argument("-y", "--vertical_resolution", help="vertical resolution", type=int, default=480)
    parser.add_argument("-z", "--rotation", help="image rotation", type=int, default=0)
    parser.add_argument("-s", "--snapshot", help="Snapshot topic(s)", nargs='+', required=True)
    parser.add_argument("-t", "--recording", help="Recording topic(s)", nargs='+', required=True)
    parser.add_argument("-n", "--name", help="Name", required=True)
    parser.add_argument("-b", "--bucket", help="S3 snapshot bucket", default=None)
    parser.add_argument("-a", "--archive_bucket", help="S3 snapshot archive bucket", default=None)
    args = parser.parse_args()

    video = Video(
        base_filename=args.name,
        rotation=args.rotation,
        horizontal_resolution=args.horizontal_resolution,
        vertical_resolution=args.vertical_resolution
    )
    video.start()

    archiver = S3Archiver(args.archive_bucket)
    archiver.start()

    subscriber = Subscriber(args.endpoint, args.rootCA, args.key, args.cert, args.clientID)

    for t in args.snapshot:
        subscriber.subscribe(t, snapshot_callback)
        time.sleep(2)  # pause

    for t in args.recording:
        subscriber.subscribe(t, recording_callback)
        time.sleep(2)  # pause

    # Loop forever
    try:
        while True:
            time.sleep(0.2)  # sleep needed because CPU race
            pass
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
