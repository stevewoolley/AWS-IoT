import threading
import RPi.GPIO as GPIO
import time


class Buzzer(threading.Thread):
    """A threaded Buzzer object"""

    def __init__(self, name, pin):
        threading.Thread.__init__(self)
        self.name = name
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
            time.sleep(0.0001)
