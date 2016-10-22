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
    result = os_execute("ip addr show %s" % interface)
    if result is not None:
        return result.split('\n')[2].strip().split(' ')[1].split('/')[0]
    else:
        return None


def connection_count():
    """Returns the number of network connections"""
    result = os_execute('netstat -tun')
    if result is not None:
        return dict(connection_count=len([x for x in result.split() if x == 'ESTABLISHED']))
    else:
        return dict(connection_count=0)


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
    for s in os_execute_shell("cat /proc/cpuinfo  | grep 'model name\|Hardware\|Serial' | uniq "):
        items[util.camel_case(s.split(':')[0])] = s.split(':')[1].replace('\t', '').replace('\n', '')
    return items

def boot_info():
    item = dict()
    item['running_duration'] = os_execute('uptime -p')
    item['start_time'] = os_execute('uptime -s')
    return dict(boot_info=item)


def memory_usage_info():
    item = dict()
    item['total'] = os_execute_shell("free -m -t | awk 'NR==2' | awk '{print $2'}")
    item['used'] = os_execute_shell("free -m -t | awk 'NR==3' | awk '{print $3'}")
    item['available'] = int(item['total']) - int(item['used'])
    return dict(memory_usage_info=item)


def os_name():
    return dict(os_name=os_execute_shell("cat /etc/*-release | grep PRETTY_NAME | cut -d= -f2").replace('"', ''))


def cpu_usage_info():
    item = dict()
    item['in_use'] = os_execute_shell("top -b -n2 | grep 'Cpu(s)'|tail -n 1 | awk '{print $2 + $4 }'")
    return dict(cpu_usage_info=item)


def cpu_processor_count():
    return os_execute_dict('nproc', 'cpu_processor_count')


def cpu_core_frequency():
    return dict(cpu_core_frequency=os_execute_shell("vcgencmd get_config arm_freq | cut -d= -f2"))


def cpu_core_volt():
    return dict(cpu_core_volt=os_execute_shell("vcgencmd measure_volts | cut -d= -f2"))


def cpu_temperature():
    temp = CPUTemperature()
    cpu_info = {'temperature': 0, 'color': 'white'}
    try:
        cpu_temp = temp.temperature
        cpu_info['temperature'] = cpu_temp
        if cpu_temp > 50:
            cpu_info['color'] = 'red'
        elif cpu_temp > 40:
            cpu_info['color'] = 'orange'
        return cpu_info
    except Exception as ex:
        print ex
    finally:
        return dict(cpu_temperature=cpu_info)


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
