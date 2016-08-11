import platform
import subprocess


def node():
    return platform.node()


def architecture():
    return platform.architecture()


def machine():
    return platform.machine()


def ip_address(interface):
    """Returns the IP address for the given interface e.g. eth0"""
    item = {interface: 'Na'}
    try:
        s = subprocess.check_output(["ip", "addr", "show", interface])
        item[interface] = s.split('\n')[2].strip().split(' ')[1].split('/')[0]
    except Exception as ex:
        print ex
    finally:
        return dict(interface=item)


def connection_count():
    """Returns the number of network connections"""
    try:
        s = subprocess.check_output(["netstat", "-tun"])
        return dict(connection_count=len([x for x in s.split() if x == 'ESTABLISHED']))
    except Exception as ex:
        print ex
        return dict(connection_count='Na')


def process_count():
    """Returns the number of processes"""
    try:
        s = subprocess.check_output(["ps", "-e"])
        return dict(process_count=len(s.split('\n')))
    except Exception as ex:
        print ex
        return dict(process_count='Na')


def cpu_generic_details():
    items = []
    try:
        items = [s.split('\t: ') for s in
                 subprocess.check_output(["cat /proc/cpuinfo  | grep 'model name\|Hardware\|Serial' | uniq "],
                                         shell=True).splitlines()]
    except Exception as ex:
        print ex
    finally:
        return items


def boot_info():
    item = {'start_time': 'Na', 'running_duration': 'Na'}
    try:
        item['running_duration'] = subprocess.check_output(['uptime -p'], shell=True).replace('\n', '')
        item['start_time'] = subprocess.check_output(['uptime -s'], shell=True).replace('\n', '')
    except Exception as ex:
        print ex
    finally:
        return dict(boot_info=item)


def memory_usage_info():
    item = {'total': 'Na', 'used': 'Na', 'available': 'Na'}
    try:
        item['total'] = subprocess.check_output(["free -m -t | awk 'NR==2' | awk '{print $2'}"], shell=True).replace(
            '\n', '')
        item['used'] = subprocess.check_output(["free -m -t | awk 'NR==3' | awk '{print $3'}"], shell=True).replace(
            '\n', '')
        item['available'] = int(item['total']) - int(item['used'])
    except Exception as ex:
        print ex
    finally:
        return dict(memory_usage_info=item)


def os_name():
    os_info = subprocess.check_output(
        "cat /etc/*-release | grep PRETTY_NAME | cut -d= -f2", shell=True).replace('\n',
                                                                                   '').replace('"', '')
    return dict(os_name=os_info)


def cpu_usage_info():
    item = {'in_use': 0}
    try:
        item['in_use'] = subprocess.check_output("top -b -n2 | grep 'Cpu(s)'|tail -n 1 | awk '{print $2 + $4 }'",
                                                 shell=True).replace('\n', '')
    except Exception as ex:
        print ex
    finally:
        return dict(cpu_usage_info=item)


def cpu_processor_count():
    proc_info = subprocess.check_output("nproc", shell=True).replace('\n', '')
    return dict(cpu_processor_count=proc_info)


def cpu_core_frequency():
    try:
        core_frequency = subprocess.check_output("vcgencmd get_config arm_freq | cut -d= -f2", shell=True).replace('\n',
                                                                                                                   '')
    except Exception as ex:
        print ex
        core_frequency = 'Na'
    finally:
        return dict(cpu_core_frequency=core_frequency)


def cpu_core_volt():
    try:
        core_volt = subprocess.check_output("vcgencmd measure_volts | cut -d= -f2", shell=True).replace('\n', '')
    except Exception as ex:
        print ex
        core_volt = 'Na'
    finally:
        return dict(cpu_core_volt=core_volt)


def cpu_temperature():
    cpu_info = {'temperature': 0, 'color': 'white'}
    try:
        cpu_temp = float(subprocess.check_output(["vcgencmd measure_temp"], shell=True).split('=')[1].split('\'')[0])
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
