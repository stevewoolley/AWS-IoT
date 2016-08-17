import threading
import time
import logging
import util
import wiringpi2 as wiringpi

LOW = 0
HIGH = 1


class Relay(threading.Thread):
    """A threaded Relay object"""

    def __init__(self, pin, name='relay', pulse_duration=1, log_level=logging.INFO):
        threading.Thread.__init__(self)
        self.name = name
        self.pin = pin
        self.pulse_duration = pulse_duration
        self.finish = False
        self.daemon = True
        self.logger = util.set_logger(level=log_level)
        self.last_reading = None

        # initialize relay
        wiringpi.wiringPiSetup()

    def pulse(self):
        # will pulse the relay for duration second(s)
        # should be sensitive for whether relay is HIGH or LOW
        value = HIGH
        opposite = LOW
        if self.reading() != LOW:
            # if relay is already high, pulse it low
            value = LOW
            opposite = HIGH
        wiringpi.pinMode(self.pin, value)
        wiringpi.digitalWrite(self.pin, value)
        time.sleep(self.pulse_duration)
        wiringpi.digitalWrite(self.pin, opposite)
        wiringpi.pinMode(self.pin, opposite)

    def reading(self):
        result = wiringpi.digitalRead(self.pin)
        self.logger.info('relay: reading: pin:%s %s' % (self.pin, result))
        return result

    def turn_on(self):
        self.switch(HIGH)

    def turn_off(self):
        self.switch(LOW)

    def switch(self, v):
        if self.reading() != v:
            self.logger.debug('relay: switch: pin:%s %s' % (self.pin, str(v)))
            wiringpi.pinMode(self.pin, v)
            wiringpi.digitalWrite(self.pin, v)
        else:
            self.logger.debug('relay: switch: pin %s ignore already %s' % (self.pin, str(v)))

    def run(self):
        while not self.finish:
            time.sleep(0.001)
