import threading
import time
import logging
import util
import wiringpi as relay


class Relay(threading.Thread):
    """A threaded Relay object"""

    ON = 1
    OFF = 0

    def __init__(self, pin, pulse_duration=1, log_level=logging.INFO):
        threading.Thread.__init__(self)
        self.pin = pin
        self.pulse_duration = pulse_duration
        self.finish = False
        self.daemon = True
        self.logger = util.set_logger(level=log_level)

        # initialize relay
        relay.wiringPiSetup()

    def pulse(self):
        # will pulse the relay for duration second(s)
        # should be sensitive for whether relay is HIGH or LOW
        self.flip()
        time.sleep(self.pulse_duration)
        self.flip()

    def reading(self):
        return relay.digitalRead(self.pin)

    def turn_on(self):
        if self.reading() == self.OFF:
            relay.pinMode(self.pin, self.ON)
            relay.digitalWrite(self.pin, self.ON)

    def turn_off(self):
        if self.reading() == self.ON:
            relay.pinMode(self.pin, self.OFF)
            relay.digitalWrite(self.pin, self.OFF)

    def flip(self):
        if self.reading() == self.ON:
            self.turn_off()
        else:
            self.turn_on()

    def run(self):
        while not self.finish:
            time.sleep(0.001)
