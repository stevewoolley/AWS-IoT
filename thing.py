#!/usr/bin/env python

import json
import argparse
import logging
import util
import boto3



class Thing:
    """A AWS IoT Thing"""

    # constants
    STATE = 'state'
    REPORTED = 'reported'
    DESIRED = 'desired'
    TIMEOUT = 'timeout'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    TIMESTAMP = 'timestamp'
    CLIENT_TOKEN = 'clientToken'
    VERSION = 'version'
    METADATA = 'metadata'
    PAYLOAD = 'payload'

    def __init__(self, name, log_level=logging.WARNING):
        self.name = name
        self._client = boto3.client('iot-data')
        self.logger = util.set_logger(level=log_level)
        self._shadow = {}
        self.properties = {}
        self.metadata = {}
        self.last_report = None
        self.last_refresh = None
        # set initial shadow
        self.refresh()

    def refresh(self):
        # query
        response = self._client.get_thing_shadow(thingName=self.name)
        self._shadow = json.loads(response[self.PAYLOAD].read().decode('utf-8'))
        # set properties
        if self.TIMESTAMP in self._shadow:
            self.last_refresh = self._shadow[self.TIMESTAMP]
        if self.STATE in self._shadow:
            if self.REPORTED in self._shadow[self.STATE]:
                self.properties = self._shadow[self.STATE][self.REPORTED]
        if self.METADATA in self._shadow:
            if self.REPORTED in self._shadow[self.METADATA]:
                self.metadata = self._shadow[self.METADATA][self.REPORTED]
                for k, v in self.metadata.iteritems():
                    if v[self.TIMESTAMP] is None or v[self.TIMESTAMP] > self.last_report:
                        self.last_report = v[self.TIMESTAMP]

    def put(self, state, obj):
        payload = {self.STATE: {state: {}}}
        for k, v in obj.iteritems():
            payload[self.STATE][state][k] = v
        self._client.update_thing_shadow(thingName=self.name, payload=json.dumps(payload))


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", help="Thing name", required=True)
    parser.add_argument("-g", "--log_level", help="log level", type=int, default=logging.WARNING)
    args = parser.parse_args()

    # initialize
    thing = Thing(args.name, args.log_level)
    print "PROPERTIES {} {}".format(args.name, thing.properties)
    print "METADATA {} {}".format(args.name, thing.metadata)
    #
    # thing.put(REPORTED, {'foo': util.now_string()})
    #
