#!/usr/bin/env python

import argparse
import util
import psutil
import datetime
import platform
from cloud_tools import Reporter

DT_FORMAT = '%Y/%m/%d %-I:%M %p %Z'


def get_rpi_cpu_temperature():
    """Returns raspberry pi cpu temperature in Centigrade"""
    temp = util.os_execute('/opt/vc/bin/vcgencmd measure_temp')
    return float(temp.split('=')[1].strip('\'C'))


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
        if platform.machine().startswith('arm') and platform.system() == 'Linux':  # raspberry pi
            properties["cpuTemp"] = get_rpi_cpu_temperature()
        properties["ramAvailable"] = int(mem.available / (1024 * 1024))
        properties["usedDiskSpaceRoot"] = int(disk.used / (1024 * 1024))
        properties["bootTime"] = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime(DT_FORMAT)
        properties["cpuLoad"] = psutil.cpu_percent(interval=3)

    if group is None or group == 'seldom':
        if platform.system() == 'Darwin':  # mac
            properties["release"] = platform.mac_ver()[0]
            properties["wlan0IpAddress"] = get_ip('wlan0')
            properties["eth0IpAddress"] = get_ip('eth0')
        elif platform.machine().startswith('arm') and platform.system() == 'Linux':  # raspberry pi
            properties["distribution"] = "{} {}".format(platform.mac_ver()[0], platform.mac_ver()[1])
            properties["en0IpAddress"] = get_ip('en0')
            properties["en1IpAddress"] = get_ip('en1')
        properties["totalDiskSpaceRoot"] = int(disk.total / (1024 * 1024))
        properties["hostname"] = platform.node()
        properties["machine"] = platform.machine()
        properties["system"] = platform.system()
        properties["cpuProcessorCount"] = psutil.cpu_count()
        properties["ramTotal"] = int(mem.total / (1024 * 1024))

    return properties


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--name", help="pi AWS thing name", required=True)
    parser.add_argument("-p", "--party", help="Monitor party", default=None)
    args = parser.parse_args()

    # Lookup system_info
    Reporter(args.name).put(Reporter.REPORTED, get_properties(args.party))
