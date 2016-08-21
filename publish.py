import argparse
import logging
import json
from publisher import Publisher

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
parser.add_argument("-r", "--rootCA", help="Root CA file path", required=True)
parser.add_argument("-c", "--cert", help="Certificate file path")
parser.add_argument("-k", "--key", help="Private key file path")
parser.add_argument("-g", "--log_level", help="log level", type=int, default=logging.INFO)
parser.add_argument("-t", "--topic", help="IoT topic", required=True)
parser.add_argument("-s", "--source", help="Source")
parser.add_argument("-m", "--message", help="Message", default='')
parser.add_argument("-i", "--clientID", help="Client ID", default='')  # empty string auto generates unique client ID
args = parser.parse_args()

data = dict()
data["alert_count"] = 5
msg = json.dumps(data)

# Publish
result = Publisher(
    args.endpoint,
    args.rootCA,
    args.key,
    args.cert
).publish(args.topic, msg)

if not result:
    exit(-1)
