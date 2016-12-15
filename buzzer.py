#!/usr/bin/env python

import threading
import RPi.GPIO as GPIO
import time
import argparse


class Buzzer(threading.Thread):
    """A threaded Buzzer object"""

    def __init__(self, pin):
        threading.Thread.__init__(self)
        self.pin = pin
        self.finish = False
        self.daemon = True

        # for GPIO numbering, choose BCM
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        # setup
        GPIO.setup(self.pin, GPIO.IN)
        GPIO.setup(self.pin, GPIO.OUT)

    def beep(self, beep_duration=0.06, quiet_duration=0.1, count=1):
        for n in range(count):
            GPIO.output(self.pin, GPIO.HIGH)
            time.sleep(beep_duration)
            GPIO.output(self.pin, GPIO.LOW)
            time.sleep(quiet_duration)

    def run(self):
        while not self.finish:
            time.sleep(0.01)


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pin", help="gpio pin (BCM)", type=int, required=True)
    parser.add_argument("-n", "--number_of_beeps", help="number of beeps", type=int, default=1)
    parser.add_argument("-d", "--beep_duration", help="time in seconds for a beep duration", type=float, default=0.06)
    parser.add_argument("-q", "--quiet_duration", help="time in seconds between beeps", type=float, default=0.1)
    args = parser.parse_args()

    buzzer = Buzzer(args.pin)
    buzzer.start()

    buzzer.beep(beep_duration=args.beep_duration, quiet_duration=args.quiet_duration, count=args.number_of_beeps)
