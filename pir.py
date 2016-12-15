import threading
import RPi.GPIO as GPIO
import time
import util


class PIR(threading.Thread):
    """A threaded PIR object"""

    def __init__(self, pin):
        threading.Thread.__init__(self)
        self.pin = pin
        self.finish = False
        self.daemon = True

        # for GPIO numbering, choose BCM
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        # initialize motion sensor
        GPIO.setup(self.pin, GPIO.IN, GPIO.PUD_DOWN)

    def movement(self):
        if GPIO.input(self.pin) == 0:  # no movement
            return False
        else:  # movement
            return True

    def reading(self):
        return GPIO.input(self.pin)

    def run(self):
        while not self.finish:
            time.sleep(0.001)
