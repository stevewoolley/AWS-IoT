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
    parser.add_argument("-q", "--queue_len",
                        help="The length of the queue used to store values read from the sensor. (1 = disabled)",
                        type=int, default=1)
    parser.add_argument("-x", "--sample_rate",
                        help="The number of values to read from the device (and append to the internal queue) per second",
                        type=float, default=100)
    parser.add_argument("-y", "--threshold",
                        help="When the mean of all values in the internal queue rises above this value, the sensor will be considered active by the is_active property, and all appropriate events will be fired",
                        type=float, default=0.5)
    args = parser.parse_args()

    pir = MotionSensor(
        args.pin,
        queue_len=args.queue_len,
        sample_rate=args.sample_rate,
        threshold=args.threshold
    )

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
