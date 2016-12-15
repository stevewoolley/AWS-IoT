#!/usr/bin/env python
import argparse
import system_info
import util
import logging
from thing import Thing


def get_properties(group):
    properties = {}
    if group is None or group == 'fresh':
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

    if group is None or group == 'seldom':
        properties["wlan0IpAddress"] = system_info.ip_address('wlan0')
        properties["eth0IpAddress"] = system_info.ip_address('eth0')
        properties["ramTotal"] = system_info.memory_usage_info()['total']
        properties["osName"] = system_info.os_name()
        properties["cpuProcessorCount"] = system_info.cpu_processor_count()
        properties["cpuCoreFrequency"] = system_info.cpu_core_frequency()

    if group is None or group == 'docker':
        docker = system_info.os_execute('docker --version')
        if docker != 'NA':
            properties["dockerVersion"] = docker
            docker_info = system_info.docker_info()
            properties["dockerContainersRunning"] = util.num(docker_info['running'])
            properties["dockerArchitecture"] = docker_info['architecture']
    return properties


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", help="pi name", required=True)
    parser.add_argument("-p", "--party", help="Monitor party", default=None)
    parser.add_argument("-g", "--log_level", help="log level", type=int, default=logging.WARNING)
    args = parser.parse_args()

    thing = Thing(args.name, args.log_level)
    thing.put(Thing.REPORTED, get_properties(args.party))
