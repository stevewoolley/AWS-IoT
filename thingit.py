#!/usr/bin/env python
import argparse
from thing import Thing
import time

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", help="Thing name", required=True)
parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
parser.add_argument("-r", "--rootCA", help="Root CA file path", required=True)
parser.add_argument("-c", "--cert", help="Certificate file path")
parser.add_argument("-k", "--key", help="Private key file path")
parser.add_argument("-m", "--message", help="Message", default=None)
args = parser.parse_args()

data = {'message': args.message}

thing = Thing(args.name, args.endpoint, args.rootCA, args.key, args.cert)
time.sleep(5)
print("RESULT 1: {} {} {}".format(thing.last_update, thing.last_refresh, thing.properties))
thing.refresh()
time.sleep(5)
print("RESULT 2: {} {} {}".format(thing.last_update, thing.last_refresh, thing.properties))