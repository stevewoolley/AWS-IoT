#!/usr/bin/env python

import argparse
import time
import sys
import json
import yaml
import logging
import psutil
import signal
import os
import subprocess
from cloud_tools import Subscriber

LOG_FILE = '/var/log/iot.log'
RECORD = 'record'
START = 'start'
STOP = 'stop'
KEY = 'key'
RASPIVID_CMD = ['/usr/bin/raspivid',
                '-o -',
                '-t', '0',
                '-vf',
                '-hf',
                '-rot', '{}'
                        '-fps', '{}',
                '-b', '{}']
FFMPEG_CMD = [
    '/usr/local/bin/ffmpeg',
    '-re',
    '-ar', '44100',
    '-ac', '2',
    '-acodec', 'pcm_s16le',
    '-f', 's16le',
    '-ac', '2',
    '-i', '/dev/zero',
    '-f', 'h264',
    '-i',
    '-',
    '-vcodec', 'copy',
    '-acodec', 'aac',
    '-ab', '128k',
    '-g', '50',
    '-strict', 'experimental',
    '-f', 'flv',
    'rtmp://a.rtmp.youtube.com/live2/{}']

streamer = None


def kill_all(p):
    # first kill children processes
    for child in psutil.Process(p).children():
        os.kill(child.pid, signal.SIGKILL)
    # now kill the parent
    os.kill(p, signal.SIGKILL)


def my_callback(client, userdata, message):
    global streamer
    logging.info("vstream_sub {} {} {}".format(message.topic, message.qos, message.payload))
    msg = json.loads(message.payload)
    # handle based on message
    if RECORD in msg:
        if msg[RECORD] == START:
            if KEY in msg:
                streamer = subprocess.Popen(
                    ' '.join(RASPIVID_CMD).format(args.rotation, args.fps, args.bitrate) + ' | ' + ' '.join(
                        FFMPEG_CMD).format(
                        msg[KEY]),
                    shell=True)
        elif msg[RECORD] == STOP:
            kill_all(streamer.pid)


if __name__ == "__main__":

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
    parser.add_argument("-i", "--clientID", help="Client ID", default='')
    parser.add_argument("-r", "--rootCA", help="Root CA file path", required=True)
    parser.add_argument("-c", "--cert", help="Certificate file path")
    parser.add_argument("-k", "--key", help="Private key file path")

    parser.add_argument("-f", "--fps", help="Frames per second to record", type=int, default=30)
    parser.add_argument("-b", "--bitrate", help="Capture bitrate. Use bits per second", type=int, default=6000000)
    parser.add_argument("-z", "--rotation", help="image rotation", type=int, default=0)

    parser.add_argument("-t", "--topic", help="MQTT topic(s)", nargs='+', required=False)

    parser.add_argument("-l", "--log_level", help="Log Level", default=logging.INFO)

    args = parser.parse_args()

    logging.basicConfig(filename=LOG_FILE, level=args.log_level)

    subscriber = Subscriber(args.endpoint, args.rootCA, args.key, args.cert, args.clientID)

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
