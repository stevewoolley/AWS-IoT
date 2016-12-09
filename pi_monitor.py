#!/usr/bin/env python
import argparse
import logging
import system_info
import util
import json
from publisher import Publisher


def get_properties():
    properties = {}
    if args.party is None or args.party == 'fresh':
        properties["cpuTemp"] = system_info.cpu_temperature()
        root_fs = util.search_list(system_info.disk_usage_list(), '/', 5)
        if root_fs:
            properties["totalDiskSpaceRoot"] = root_fs[1]
            properties["usedDiskSpaceRoot"] = root_fs[2]
        properties["networkConnections"] = system_info.connection_count()
        properties["ramAvailable"] = system_info.memory_usage_info()['available']
        properties["processCount"] = system_info.process_count()
        properties["upTime"] = system_info.boot_info()['running_duration']
        properties["cpuLoad"] = system_info.cpu_usage_info()

    if args.party is None or args.party == 'seldom':
        properties["wlan0IpAddress"] = system_info.ip_address('wlan0')
        properties["eth0IpAddress"] = system_info.ip_address('eth0')
        properties["ramTotal"] = system_info.memory_usage_info()['total']
        properties["osName"] = system_info.os_name()
        properties["cpuProcessorCount"] = system_info.cpu_processor_count()
        properties["cpuCoreFrequency"] = system_info.cpu_core_frequency()

    if args.party is None or args.party == 'docker':
        docker = system_info.os_execute('docker --version')
        if docker != 'NA':
            properties["dockerVersion"] = docker
            docker_info = system_info.docker_info()
            properties["dockerContainersRunning"] = util.num(docker_info['running'])
            properties["dockerArchitecture"] = docker_info['architecture']
    return properties


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
parser.add_argument("-p", "--party", help="monitor party", default=None)
args = parser.parse_args()

# Lookup system_info
data = {'state': {'reported': get_properties()}}
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
    print "ERROR: publish {} {}".format(args.topic, ex.message)
