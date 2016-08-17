import threading
import RPi.GPIO as GPIO
import time
import logging
import util


class LED(threading.Thread):
    """A threaded LED object"""
    state = 0
    cycle = 2.0

    def __init__(self, name, pin, log_level=logging.INFO):
        threading.Thread.__init__(self)
        self.name = name
        self.pin = pin
        self.finish = False
        self.daemon = True

        # set logger
        self.logger = util.set_logger(level=log_level)

        # for GPIO numbering, choose BCM
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        # set pin
        GPIO.setup(self.pin, GPIO.OUT)
        GPIO.output(self.pin, False)  # on start , turn LED off

    def set_led(self, value):
        self.state = value

    def run(self):
        while not self.finish:
            try:
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
            except Exception as ex:
                self.logger.warning("led: IGNORE: %s" % ex.message)
