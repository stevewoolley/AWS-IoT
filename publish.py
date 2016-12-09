#!/usr/bin/env python
import argparse
import logging
import json
import time
import util
from publisher import Publisher

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
parser.add_argument("-r", "--rootCA", help="Root CA file path", required=True)
parser.add_argument("-c", "--cert", help="Certificate file path")
parser.add_argument("-k", "--key", help="Private key file path")
parser.add_argument("-g", "--log_level", help="log level", type=int, default=logging.INFO)
parser.add_argument("-t", "--topic", help="MQTT topic(s)", nargs='+', required=True)
parser.add_argument("-s", "--source", help="Source")
parser.add_argument("-m", "--message", help="Message", default='')
parser.add_argument("-i", "--clientID", help="Client ID", default='')  # empty string auto generates unique client ID
parser.add_argument("-w", "--wait", help="seconds to sleep between publish(s)", type=int, default=60)
args = parser.parse_args()

data = dict()
data['message'] = args.message
msg = json.dumps(data)

# Publish
while True:
    obj = []
    for t in args.topic:
        obj.append({'topic': t, 'payload': msg})
    try:
        Publisher(
            args.endpoint,
            args.rootCA,
            args.key,
            args.cert
        ).publish_multiple(obj)
        print("PUBLISH {} {}".format(util.now_string(),obj))

    except Exception as ex:
        print("ERROR publish {}".format(ex.message))
    time.sleep(args.wait)

