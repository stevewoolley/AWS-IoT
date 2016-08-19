import threading
import RPi.GPIO as GPIO
import time


class Sensor(threading.Thread):
    """A threaded Sensor object"""

    LOW = GPIO.LOW
    HIGH = GPIO.HIGH

    def __init__(self, pin, name='sensor'):
        threading.Thread.__init__(self)
        self.name = name
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
