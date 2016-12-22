#!/usr/bin/env python

import argparse
import util
import psutil
import datetime
import platform
from cloud_tools import Publisher

DT_FORMAT = '%Y/%m/%d %-I:%M %p %Z'
TOPIC = "$aws/things/{}/shadow/update"


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
            properties["distribution"] = "{} {}".format(platform.dist()[0], platform.dist()[1])
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
    parser.add_argument("-e", "--endpoint", help="AWS IoT endpoint", required=True)
    parser.add_argument("-r", "--rootCA", help="Root CA file path", required=True)
    parser.add_argument("-c", "--cert", help="Certificate file path")
    parser.add_argument("-k", "--key", help="Private key file path")
    parser.add_argument("-i", "--clientID", help="Client ID", default='')
    parser.add_argument("-s", "--source", help="Source", required=True)
    parser.add_argument("-p", "--party", help="Monitor party", default=None)
    args = parser.parse_args()

    Publisher(
        args.endpoint,
        args.rootCA,
        args.key,
        args.cert,
        clientID=args.clientID
    ).report(TOPIC.format(args.source), get_properties(args.party))
