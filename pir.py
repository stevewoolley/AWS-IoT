import threading
import RPi.GPIO as GPIO
import time
import logging
import util


class PIR(threading.Thread):
    """A threaded PIR object"""

    def __init__(self, pin, name='pir', log_level=logging.INFO):
        threading.Thread.__init__(self)
        self.name = name
        self.pin = pin
        self.finish = False
        self.daemon = True
        self.logger = util.set_logger(level=log_level)
        self.last_reading = None

        # for GPIO numbering, choose BCM
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        # initialize motion sensor
        GPIO.setup(self.pin, GPIO.IN, GPIO.PUD_DOWN)

    def detects_movement(self):
        value = GPIO.input(self.pin)
        if value != self.last_reading:
            self.logger.debug('PIR: %s %s' % (self.name, value))
            self.last_reading = value
        return value

    def run(self):
        while not self.finish:
            time.sleep(0.001)
