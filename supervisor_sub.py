#!/usr/bin/env python

import argparse
import time
import sys
import json
import xmlrpclib
import logging
from cloud_tools import Subscriber

LOG_FILE = '/var/log/iot.log'
PROCESS = 'process'
CMD = 'command'


def my_callback(client, userdata, message):
    logging.info("supervisor_sub {} {} {}".format(message.topic, message.qos, message.payload))
    msg = json.loads(message.payload)
    try:
        server = xmlrpclib.Server('http://localhost:9001/RPC2')
        if PROCESS in msg:
            if CMD in msg:
                if msg[CMD] == 'stop':
                    server.supervisor.stopProcess(msg[PROCESS])
                elif msg[CMD] == 'start':
                    server.supervisor.startProcess(msg[PROCESS])
                elif msg[CMD] == 'restart':
                    server.supervisor.stopProcess(msg[PROCESS])
                    time.sleep(1)
                    server.supervisor.startProcess(msg[PROCESS])
            else:
                logging.info("supervisor_sub {}".format(server.supervisor.getProcessInfo(msg[PROCESS])))
        else:
            logging.info("supervisor_sub {}".format(server.supervisor.getAllProcessInfo()))
    except:
        logging.error("supervisor_sub {}".format(sys.exc_info()[0]))


if __name__ == "__main__":

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
    parser.add_argument("-i", "--clientID", help="Client ID", default='')
    parser.add_argument("-r", "--rootCA", help="Root CA file path", required=True)
    parser.add_argument("-c", "--cert", help="Certificate file path")
    parser.add_argument("-k", "--key", help="Private key file path")

    parser.add_argument("-t", "--topic", help="MQTT topic(s)", nargs='+', required=False)

    parser.add_argument("-l", "--log_level", help="Log Level", default=logging.INFO)

    args = parser.parse_args()

    logging.basicConfig(filename=LOG_FILE, level=args.log_level)

    subscriber = Subscriber(args.endpoint, args.rootCA, args.key, args.cert, args.clientID)

    for t in args.topic:
        logging.info("Subscribing to {}".format(t))
        subscriber.subscribe(t, my_callback)
        time.sleep(2)  # pause

    # Loop forever
    try:
        while True:
            time.sleep(0.2)  # sleep needed because CPU race
            pass
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
