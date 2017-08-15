#!/usr/bin/env python

import argparse
from cloud_tools import Publisher

if __name__ == "__main__":

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
    parser.add_argument("-i", "--clientID", help="Client ID", default=None)
    parser.add_argument("-r", "--rootCA", help="Root CA file path", required=True)
    parser.add_argument("-c", "--cert", help="Certificate file path")
    parser.add_argument("-k", "--key", help="Private key file path")

    parser.add_argument("-t", "--topic", help="MQTT topic(s)", nargs='+', required=False)
    parser.add_argument("-s", "--source", help="source", default='message')
    parser.add_argument("-v", "--value", help="value", default='Foo')
    args = parser.parse_args()

    for t in args.topic:
        Publisher(args.endpoint, args.rootCA, args.key, args.cert, clientID=args.clientID).report(t,
                                                                                                  {
                                                                                                      args.source: args.value})
