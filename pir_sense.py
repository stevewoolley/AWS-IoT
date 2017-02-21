#!/usr/bin/env python

import argparse
import time
from datetime import datetime
import sys
from gpiozero import MotionSensor

if __name__ == "__main__":

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pin", help="gpio pin (using BCM numbering)", type=int, required=True)
    args = parser.parse_args()

    pir = MotionSensor(args.pin)

    try:
        motion = False
        while True:
            if motion is False and pir.motion_detected:
                motion = True
                print("MOTION DETECTED {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            elif motion is True and not pir.motion_detected:
                motion = False
                print("STILL {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            time.sleep(0.1)
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
