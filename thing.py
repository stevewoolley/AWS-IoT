#!/usr/bin/env python

import json
import argparse
import logging
import util
import boto3

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


class Thing:
    """A AWS IoT Thing"""

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
        self._shadow = json.loads(response['payload'].read().decode('utf-8'))
        # set properties
        if TIMESTAMP in self._shadow:
            self.last_refresh = self._shadow[TIMESTAMP]
        if STATE in self._shadow:
            if REPORTED in self._shadow[STATE]:
                self.properties = self._shadow[STATE][REPORTED]
        if METADATA in self._shadow:
            if REPORTED in self._shadow[METADATA]:
                self.metadata = self._shadow[METADATA][REPORTED]
                for k, v in self.metadata.iteritems():
                    if v[TIMESTAMP] is None or v[TIMESTAMP] > self.last_report:
                        self.last_report = v[TIMESTAMP]

    def put(self, state, obj):
        payload = {STATE: {state: {}}}
        for k, v in obj.iteritems():
            payload[STATE][state][k] = v
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
