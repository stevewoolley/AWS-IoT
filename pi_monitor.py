#!/usr/bin/env python

import argparse
import system_info
import util
import psutil
import datetime
import platform
from cloud_tools import Reporter

DT_FORMAT = '%Y/%m/%d %-I:%M %p %Z'


def get_ip(i):
    try:
        for k in psutil.net_if_addrs()[i]:
            family, address, netmask, broadcast, ptp = k
            if family == 2:
                return address
        return None
    except Exception as ex:
        return None


def get_properties(group):
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    properties = {}
    if group is None or group == 'fresh':
        properties["cpuTemp"] = system_info.cpu_temperature()
        properties["ramAvailable"] = int(mem.available / (1024 * 1024))
        properties["totalDiskSpaceRoot"] = int(disk.total / (1024 * 1024))
        properties["usedDiskSpaceRoot"] = int(disk.used / (1024 * 1024))
        properties["bootTime"] = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime(DT_FORMAT)
        properties["cpuLoad"] = psutil.cpu_percent(interval=2)

    if group is None or group == 'seldom':
        properties["wlan0IpAddress"] = get_ip('wlan0')
        properties["eth0IpAddress"] = get_ip('eth0')
        properties["release"] = platform.mac_ver()[0]
        properties["hostname"] = platform.node()
        properties["machine"] = platform.machine()
        properties["system"] = platform.system()
        properties["cpuProcessorCount"] = psutil.cpu_count()
        properties["ramTotal"] = int(mem.total / (1024 * 1024))

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
    parser.add_argument("-n", "--name", help="pi AWS thing name", required=True)
    parser.add_argument("-p", "--party", help="Monitor party", default=None)
    args = parser.parse_args()

    # Lookup system_info
    Reporter(args.name).put(Reporter.REPORTED, get_properties(args.party))
