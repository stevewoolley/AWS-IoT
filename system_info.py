import platform
import subprocess
import util
from gpiozero import CPUTemperature


def node():
    return platform.node()


def architecture():
    return platform.architecture()


def machine():
    return platform.machine()


def ip_address(interface):
    """Returns the IP address for the given interface e.g. eth0"""
    result = os_execute("ip addr show %{}".format(interface))
    if result is not None:
        return result.split('\n')[2].strip().split(' ')[1].split('/')[0]
    else:
        return None


def connection_count():
    """Returns the number of network connections"""
    result = os_execute('netstat -tun')
    if result is not None:
        return len([x for x in result.split() if x == 'ESTABLISHED'])
    else:
        return 0


def docker_info():
    """Returns docker information"""
    result = dict()
    try:
        s = os_execute('docker info')
        for e in s.splitlines():
            p = e.split(':')
            if len(p) == 2:
                result[util.camel_case(p[0])] = p[1].strip()
        return result
    except Exception as ex:
        return result


def os_execute(s):
    """Returns string result of os call"""
    try:
        result = subprocess.check_output(s.split()).rstrip('\n')
        return result
    except Exception as ex:
        return None


def os_execute_shell(s):
    """Returns string result of os call"""
    try:
        result = subprocess.check_output([s], shell=True).rstrip('\n')
        return result
    except Exception as ex:
        return None


def os_execute_dict(s, k):
    """Returns dict result of os call"""
    return {k, os_execute(s)}


def process_count():
    """Returns the number of processes"""
    result = os_execute('ps -e')
    if result is not None:
        return len(result.split('\n')) - 1
    else:
        return 0


def cpu_generic_details():
    items = dict()
    for s in os_execute_shell("cat /proc/cpuinfo  | grep 'model name\|Hardware\|Serial' | uniq ").split('\n'):
        items[util.camel_case(s.split(':')[0])] = s.split(':')[1].replace('\t', '').strip()
    return items


def boot_info():
    items = dict()
    items['running_duration'] = os_execute('uptime -p')
    items['start_time'] = os_execute('uptime -s')
    return items


def memory_usage_info():
    items = dict()
    items['total'] = util.num(os_execute_shell("free -m -t | awk 'NR==2' | awk '{print $2'}"))
    items['used'] = util.num(os_execute_shell("free -m -t | awk 'NR==3' | awk '{print $3'}"))
    items['available'] = int(items['total']) - int(items['used'])
    return items


def os_name():
    return os_execute_shell("cat /etc/*-release | grep PRETTY_NAME | cut -d= -f2").replace('"', '')


def cpu_usage_info():
    return util.num(os_execute_shell("top -b -n2 | grep 'Cpu(s)'|tail -n 1 | awk '{print $2 + $4 }'"))


def cpu_processor_count():
    return util.num(os_execute('nproc'))


def cpu_core_frequency():
    return util.num(os_execute_shell("vcgencmd get_config arm_freq | cut -d= -f2"))


def cpu_core_volt():
    return os_execute_shell("vcgencmd measure_volts | cut -d= -f2")


def cpu_temperature():
    return CPUTemperature().temperature


def disk_usage_list():
    items = []
    try:
        items = [s.split() for s in subprocess.check_output(['df', '-h'], universal_newlines=True).splitlines()]
    except Exception as ex:
        print ex
    finally:
        return items[1:]


def running_process_list():
    items = []
    try:
        items = [s.split() for s in subprocess.check_output(["ps -Ao user,pid,pcpu,pmem,comm,lstart --sort=-pcpu"],
                                                            shell=True).splitlines()]
    except Exception as ex:
        print ex
    finally:
        return items[1:]
