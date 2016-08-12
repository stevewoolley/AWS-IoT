#!/usr/bin/env python

import argparse
import logging
import system_info
import util
from publisher import Publisher

# parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
parser.add_argument("-r", "--rootCA", help="Root CA file path", required=True)
parser.add_argument("-c", "--cert", help="Certificate file path")
parser.add_argument("-k", "--key", help="Private key file path")
parser.add_argument("-w", "--websocket", help="Use MQTT over WebSocket", action='store_true')
parser.add_argument("-g", "--log_level", help="log level", type=int, default=logging.INFO)
parser.add_argument("-t", "--topic", help="IoT topic", required=True)
parser.add_argument("-o", "--topic2", help="Additional IoT topic")
parser.add_argument("-i", "--clientID", help="Client ID", default='')  # empty string auto generates unique client ID
args = parser.parse_args()

# Lookup system_info
data = dict()
data["state"] = {}
data["state"]["reported"] = {}
data["state"]["reported"]["cpuTemp"] = system_info.cpu_temperature()['cpu_temperature']['temperature']
data["state"]["reported"]["wlan0IpAddress"] = system_info.ip_address('wlan0')['interface']['wlan0']
data["state"]["reported"]["eth0IpAddress"] = system_info.ip_address('eth0')['interface']['eth0']
root_fs = util.search_list(system_info.disk_usage_list(), '/', 5)
if root_fs:
    data["state"]["reported"]["totalDiskSpaceRoot"] = root_fs[1]
    data["state"]["reported"]["usedDiskSpaceRoot"] = root_fs[2]
data["state"]["reported"]["networkConnections"] = system_info.connection_count()['connection_count']
data["state"]["reported"]["ramTotal"] = system_info.memory_usage_info()['memory_usage_info']['total']
data["state"]["reported"]["ramAvailable"] = system_info.memory_usage_info()['memory_usage_info']['available']
data["state"]["reported"]["processCount"] = system_info.process_count()['process_count']
data["state"]["reported"]["upTime"] = system_info.boot_info()['boot_info']['running_duration']
data["state"]["reported"]["cpuLoad"] = system_info.cpu_usage_info()['cpu_usage_info']['in_use']

# Publish

try:
    if args.topic2 is not None:
        Publisher(
            args.endpoint,
            args.rootCA,
            args.key,
            args.cert
        ).publish(args.topic, str(data))
    else:
        Publisher(
            args.endpoint,
            args.rootCA,
            args.key,
            args.cert
        ).publish_multiple([{'topic': args.topic, 'payload': str(data)}, {'topic': args.topic2, 'payload': str(data)}])
except Exception as ex:
    print "ERROR: publish %s %s" % (args.topic, ex.message)
