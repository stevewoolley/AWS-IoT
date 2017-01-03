#!/usr/bin/env python

import argparse
import util
import psutil
import datetime
import platform
import logging
from cloud_tools import Publisher

DT_FORMAT = '%Y/%m/%d %-I:%M %p %Z'
TOPIC = "$aws/things/{}/shadow/update"


def get_rpi_cpu_temperature():
    """Returns raspberry pi cpu temperature in Centigrade"""
    temp = util.os_execute('/opt/vc/bin/vcgencmd measure_temp')
    return float(temp.split('=')[1].strip('\'C'))


def get_ip(i):
    if i in psutil.net_if_addrs():
        try:
            for k in psutil.net_if_addrs()[i]:
                family, address, netmask, broadcast, ptp = k
                if family == 2:
                    return address
            return None
        except Exception as ex:
            logging.debug(ex.message)
            return None
    else:
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
        elif platform.machine().startswith('arm') and platform.system() == 'Linux':  # raspberry pi
            properties["distribution"] = "{} {}".format(platform.dist()[0], platform.dist()[1])
        for i in ['en0', 'en1', 'en2', 'en3', 'wlan0', 'wlan1', 'eth0', 'eth1']:
            properties["{}IpAddress".format(i)] = get_ip(i)
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
    parser.add_argument("-c", "--cert", help="Certificate file path", required=True)
    parser.add_argument("-k", "--key", help="Private key file path", required=True)
    parser.add_argument("-i", "--clientID", help="Client ID", default=None)
    parser.add_argument("-s", "--source", help="Source", default=platform.node().split('.')[0])
    parser.add_argument("-p", "--party", help="Monitor party", default=None)
    parser.add_argument("-l", "--log_level", help="Log Level", default=logging.WARNING)
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level)
    logger = logging.getLogger(__name__)
    logging.debug("monitor init")

    Publisher(
        args.endpoint,
        args.rootCA,
        args.key,
        args.cert,
        clientID=args.clientID,
        log_level=args.log_level
    ).report(TOPIC.format(args.source), get_properties(args.party))
