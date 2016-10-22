#!/usr/bin/env python

import argparse
import logging
import system_info
import util
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
parser.add_argument("-o", "--topic2", help="Additional IoT topic")
parser.add_argument("-i", "--clientID", help="Client ID", default='')  # empty string auto generates unique client ID
parser.add_argument("-p", "--party", help="monitor party", default=None)  # empty string auto generates unique client ID
args = parser.parse_args()

# Lookup system_info
data = {'state': {'reported': {}}}
if args.party is None or args.party == 'fresh':
    data["state"]["reported"]["cpuTemp"] = system_info.cpu_temperature()
    root_fs = util.search_list(system_info.disk_usage_list(), '/', 5)
    if root_fs:
        data["state"]["reported"]["totalDiskSpaceRoot"] = root_fs[1]
        data["state"]["reported"]["usedDiskSpaceRoot"] = root_fs[2]
    data["state"]["reported"]["networkConnections"] = system_info.connection_count()
    data["state"]["reported"]["ramAvailable"] = system_info.memory_usage_info()['available']
    data["state"]["reported"]["processCount"] = system_info.process_count()
    data["state"]["reported"]["upTime"] = system_info.boot_info()['running_duration']
    data["state"]["reported"]["cpuLoad"] = system_info.cpu_usage_info()

if args.party is None or args.party == 'seldom':
    data["state"]["reported"]["wlan0IpAddress"] = system_info.ip_address('wlan0')
    data["state"]["reported"]["eth0IpAddress"] = system_info.ip_address('eth0')
    data["state"]["reported"]["ramTotal"] = system_info.memory_usage_info()['total']
    data["state"]["reported"]["osName"] = system_info.os_name()
    data["state"]["reported"]["cpuProcessorCount"] = system_info.cpu_processor_count()
    data["state"]["reported"]["cpuCoreFrequency"] = system_info.cpu_core_frequency()

if args.party is None or args.party == 'docker':
    docker = system_info.os_execute('docker --version')
    if docker != 'NA':
        data["state"]["reported"]["dockerVersion"] = docker
        docker_info = system_info.docker_info()
        data["state"]["reported"]["dockerContainersRunning"] = util.num(docker_info['running'])

msg = json.dumps(data)

try:
    if args.topic2 is None:
        Publisher(
            args.endpoint,
            args.rootCA,
            args.key,
            args.cert
        ).publish(args.topic, msg)
    else:
        Publisher(
            args.endpoint,
            args.rootCA,
            args.key,
            args.cert
        ).publish_multiple([{'topic': args.topic, 'payload': msg}, {'topic': args.topic2, 'payload': msg}])
except Exception as ex:
    print "ERROR: publish %s %s" % (args.topic, ex.message)
