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
parser.add_argument("-t", "--topic", help="MQTT topic(s)", nargs='+', required=True)
parser.add_argument("-s", "--sleep", help="Sleep seconds", default=60)
parser.add_argument("-g", "--log_level", help="log level", type=int, default=logging.INFO)
args = parser.parse_args()

SNAPSHOT = 'snapshot'

data = dict()
msg = json.dumps(data)

# Publish
while True:
    for t in args.topic:
        result = Publisher(
            args.endpoint,
            args.rootCA,
            args.key,
            args.cert
        ).publish(t, msg)
        print("%s %s %s" % (util.now_string(), t, result))
    time.sleep(args.sleep)

if not result:
    exit(-1)
