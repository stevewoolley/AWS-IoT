#!/usr/bin/env python

import time
import json
import argparse
import sys
import logging
import util
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient

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

    def __init__(self, name, endpoint, root_ca, key=None, cert=None, web_socket=False, client_id='',
                 log_level=logging.WARNING):
        self.name = name
        self._client = None
        self._shadow = None
        self.connected = False
        self.properties = {}
        self.last_refresh = None
        self.last_report = None
        self.client_token = None
        self.version = None
        self.metadata = None
        self.token = None
        self.logger = util.set_logger(level=log_level)

        # setup client connection
        if web_socket:
            self._client = AWSIoTMQTTShadowClient(client_id, useWebsocket=web_socket)
            self._client.configureEndpoint(endpoint, 443)
            self._client.configureCredentials(root_ca)
        else:
            self._client = AWSIoTMQTTShadowClient(client_id)
            self._client.configureEndpoint(endpoint, 8883)
            self._client.configureCredentials(root_ca, key, cert)
        self._client.configureConnectDisconnectTimeout(10)  # 10 sec
        self._client.configureMQTTOperationTimeout(5)  # 5 sec

    def shadow_callback_update(self, payload, response_status, token):
        self.logger.info("UPDATE RESPONSE {} {}".format(args.name, response_status))
        if response_status == ACCEPTED:
            msg = json.loads(payload)
            self.token = token
            self.logger.info("UPDATE ACCEPTED {} {}".format(args.name, msg))

    def shadow_callback_get(self, payload, response_status, token):
        self.logger.info("GET RESPONSE {} {}".format(args.name, response_status))
        if response_status == ACCEPTED:
            msg = json.loads(payload)
            self.last_refresh = msg[TIMESTAMP]
            self.client_token = msg[CLIENT_TOKEN]
            self.properties = msg[STATE][REPORTED]
            self.version = msg[VERSION]
            self.metadata = msg[METADATA][REPORTED]
            self.token = token
            for k, v in self.metadata.iteritems():
                if v[TIMESTAMP] is None or v[TIMESTAMP] > self.last_report:
                    self.last_report = v[TIMESTAMP]
            self.logger.info("GET ACCEPTED {} {}".format(args.name, msg))

    def shadow_callback_delete(self, payload, response_status, token):
        self.logger.info("DELETE RESPONSE {} {}".format(args.name, response_status))
        if response_status == ACCEPTED:
            msg = json.loads(payload)
            self.token = token
            self.logger.info("DELETE ACCEPTED {} {}".format(args.name, msg))

    def _connect(self):
        if not self.connected:
            self._client.connect()
            self._shadow = self._client.createShadowHandlerWithName(self.name, True)
            self.connected = True

    def put(self, properties, state=REPORTED):
        self._connect()
        # self._shadow.shadowDelete(self.shadow_callback_delete, 5)  # Delete shadow JSON doc
        payload = {STATE: {state: {}}}
        for k, v in properties.iteritems():
            payload[STATE][state][k] = v
        self._shadow.shadowUpdate(json.dumps(payload), self.shadow_callback_update, 30)

    def refresh(self):
        self._connect()
        self._shadow.shadowGet(self.shadow_callback_get, 30)


if __name__ == "__main__":

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", help="Thing name", required=True)
    parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
    parser.add_argument("-r", "--root_ca", help="Root CA file path", required=True)
    parser.add_argument("-c", "--cert", help="Certificate file path")
    parser.add_argument("-k", "--key", help="Private key file path")
    parser.add_argument("-w", "--web_socket", help="Use web socket", action='store_true')
    parser.add_argument("-i", "--client_id", help="Client ID", default='')
    parser.add_argument("-g", "--log_level", help="log level", type=int, default=logging.WARNING)
    args = parser.parse_args()

    # initialize
    thing = Thing(args.name, args.endpoint, args.root_ca, args.key, args.cert, args.web_socket, args.client_id,
                  args.log_level)

    try:
        while True:
            time.sleep(60)
            thing.refresh()
            pass
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
