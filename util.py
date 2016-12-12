import logging
import sys
import os
import subprocess as sp
import time
import datetime


def convert_celsius_to_fahrenheit(c):
    return 9.0 / 5.0 * c + 32


def camel_case(s):
    s = s.title().replace(' ', '').replace('\t', '').replace('\n', '')
    return s[0].lower() + s[1:]


def set_logger(name='iot', level=logging.INFO):
    """Set logger to write logs to /var/log/NAME.log If not writeable, try /tmp/NAME.log"""
    fname = "/var/log/{}.log".format(name)
    if not os.access(fname, os.W_OK):
        fname = "/tmp/{}.log".format(name)
    logging.basicConfig(level=level,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        filename=fname,
                        filemode='a')

    return logging.getLogger()


def search_list(l, search_string, idx):
    if idx > len(l) - 1:
        return None
    for sublist in l:
        if sublist[idx] == search_string:
            return sublist
    return None


def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)


def move_to_s3(filename, *args):
    try:
        cmd = ['/usr/bin/aws',
               's3',
               'mv',
               filename,
               os.path.join('s3://', *args)]
        pipe = sp.Popen(cmd, stdin=sp.PIPE, stderr=sp.PIPE)  # mv snapshot.png to s3
    except Exception as e:
        print >> sys.stderr, 'ERROR util move_to_s3 {}'.format(e.message)


def copy_to_s3(filename, *args):
    try:
        cmd = ['/usr/bin/aws',
               's3',
               'cp',
               filename,
               os.path.join('s3://', *args)]
        pipe = sp.Popen(cmd, stdin=sp.PIPE, stderr=sp.PIPE)  # mv snapshot.png to s3
    except Exception as e:
        print >> sys.stderr, 'ERROR util copy_to_s3 {}'.format(e.message)


def annotate_image(filename, msg, font="/usr/share/fonts/truetype/msttcorefonts/arial.ttf", font_size="24",
                   font_color="white", geometry="+25+25"):
    try:
        cmd = ['/usr/bin/convert',
               filename,
               "-font", font,
               "-pointsize", font_size,
               "-fill", font_color,
               "-annotate", geometry, msg,
               filename
               ]
        pipe = sp.Popen(cmd, stdin=sp.PIPE, stderr=sp.PIPE)  # mv snapshot.png to s3
    except Exception as e:
        print >> sys.stderr, 'ERROR util annotate_image {} {}'.format(filename, e.message)


def generate_thumbnail(from_filename, to_filename='thumbnail.png'):
    if from_filename is not None:
        try:
            cmd = ['/usr/bin/ffmpegthumbnailer',
                   '-i', from_filename,
                   '-f',
                   '-w',
                   '-s', '0',
                   '-t', '50%',
                   '-o', to_filename]
            time.sleep(0.5)  # give some time to complete file write
            pipe = sp.Popen(cmd, stdin=sp.PIPE, stderr=sp.PIPE)  # write thumbnail.png
        except Exception as ex:
            print >> sys.stderr, 'generate_thumbnail {} {} {}'.format(from_filename, to_filename, ex.message)


def file_name(suffix, *args):
    return '_'.join(args) + '.' + suffix


def full_path(*args):
    return '/'.join(args)


def now_string():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def is_locked(filepath):
    """Checks if a file is locked by opening it in append mode.
    If no exception thrown, then the file is not locked.
    """
    locked = None
    if os.path.exists(filepath):
        try:
            os.rename(filepath, filepath)
            locked = False
        except OSError as ex:
            locked = True
            print >> sys.stderr, "util file_locked {} {}".format(filepath, ex.message)
    return locked


def merge_dicts(*dict_args):
    '''
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    '''
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result
