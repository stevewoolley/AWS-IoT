#!/usr/bin/env python

import argparse
import util
import platform
import psutil
import datetime
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


def docker_info():
    """Returns docker information"""
    result = dict()
    try:
        s = util.os_execute('/usr/local/bin/docker info')
        for e in s.splitlines():
            p = e.split(':')
            if len(p) == 2:
                result[util.camel_case(p[0])] = p[1].strip()
        return result
    except Exception as ex:
        return result


def get_properties(group):
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    properties = {}
    if group is None or group == 'fresh':
        properties["ramAvailable"] = int(mem.available / (1024 * 1024))
        properties["totalDiskSpaceRoot"] = int(disk.total / (1024 * 1024))
        properties["usedDiskSpaceRoot"] = int(disk.used / (1024 * 1024))
        properties["bootTime"] = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime(DT_FORMAT)
        properties["cpuLoad"] = psutil.cpu_percent(interval=2)

    if group is None or group == 'seldom':
        properties["en0IpAddress"] = get_ip('en0')
        properties["en1IpAddress"] = get_ip('en1')
        properties["release"] = platform.mac_ver()[0]
        properties["hostname"] = platform.node()
        properties["machine"] = platform.machine()
        properties["system"] = platform.system()
        properties["cpuProcessorCount"] = psutil.cpu_count()
        properties["ramTotal"] = int(mem.total / (1024 * 1024))

    if group is None or group == 'docker':
        docker = util.os_execute('/usr/local/bin/docker --version')
        if docker != 'NA':
            properties["dockerVersion"] = docker
            di = docker_info()
            properties["dockerContainersRunning"] = util.num(di['running'])
            properties["dockerArchitecture"] = di['architecture']
    return properties


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", help="pi AWS thing name", required=True)
    parser.add_argument("-p", "--party", help="Monitor party", default=None)
    args = parser.parse_args()
    Reporter(args.name).put(Reporter.REPORTED, get_properties(args.party))
