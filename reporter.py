#!/usr/bin/env python

import argparse
from cloud_tools import Reporter

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--name", help="Thing name", required=True)
args = parser.parse_args()

# initialize
thing = Reporter(args.name)
print "PROPERTIES {} {}".format(args.name, thing.properties)
print "METADATA {} {}".format(args.name, thing.metadata)
#
# thing.put(REPORTED, {'foo': util.now_string()})
#
