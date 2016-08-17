import threading
import RPi.GPIO as GPIO
import time
import logging
import util


class Sensor(threading.Thread):
    """A threaded Sensor object"""

    LOW = GPIO.LOW
    HIGH = GPIO.HIGH

    def __init__(self, pin, name='sensor', log_level=logging.INFO):
        threading.Thread.__init__(self)
        self.name = name
        self.pin = pin
        self.finish = False
        self.daemon = True
        self.logger = util.set_logger(level=log_level)
        self.last_reading = None

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def reading(self):
        value = GPIO.input(self.pin)
        if value != self.last_reading:
            self.logger.debug('Sensor: reading_changed: %s %s' % (self.name, value))
            self.last_reading = value
        return value

    def run(self):
        while not self.finish:
            time.sleep(0.001)
