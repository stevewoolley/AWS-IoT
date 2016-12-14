import threading
import time
from gpiozero import LED


class LED(threading.Thread):
    """A threaded LED object"""
    CYCLE = 2.0

    def __init__(self, pin):
        threading.Thread.__init__(self)
        self.pin = pin
        self._led = LED(self.pin)
        self.finish = False
        self.daemon = True


    def set_led(self, value):
        self.state = value

    def flash(self, count=2):
        GPIO.output(self.pin, False)
        for num in range(0, count):
            GPIO.output(self.pin, True)
            time.sleep(self.cycle / (self.state * 2))
            GPIO.output(self.pin, False)
            time.sleep(self.cycle / (self.state * 2))

    def run(self):
        while not self.finish:
            if self.state == 0:
                GPIO.output(self.pin, False)
            elif self.state == 1:
                GPIO.output(self.pin, True)
            elif self.state > 1:
                GPIO.output(self.pin, True)
                time.sleep(self.cycle / (self.state * 2))
                GPIO.output(self.pin, False)
                time.sleep(self.cycle / (self.state * 2))
            time.sleep(.10)
