#!/usr/bin/env python
import threading
import RPi.GPIO as GPIO
import time
import sys
import argparse


class Sensor(threading.Thread):
    """A threaded Sensor object"""

    LOW = GPIO.LOW
    HIGH = GPIO.HIGH

    def __init__(self, pin):
        threading.Thread.__init__(self)
        self.pin = pin
        self.finish = False
        self.daemon = True
        self.last_reading = None

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def reading(self):
        value = GPIO.input(self.pin)
        if value != self.last_reading:
            self.last_reading = value
        return value

    def run(self):
        while not self.finish:
            time.sleep(0.001)


if __name__ == "__main__":

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pin", help="gpio pin (BCM)", type=int, required=True)
    args = parser.parse_args()

    sensor = Sensor(args.pin)
    sensor.start()

    # Loop forever
    last_state = None
    try:
        while True:
            current_state = sensor.reading()
            if current_state != last_state:
                print("sensor pin:{} state:{}".format(args.pin, current_state))
                last_state = current_state  # reset state value
            time.sleep(0.1)  # sleep needed because CPU race
            pass
    except (KeyboardInterrupt, SystemExit):
        sys.exit()



from gpiozero import Button
from signal import pause



