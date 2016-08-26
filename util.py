import logging
import sys
import os
import subprocess as sp
import time
import datetime


def set_logger(name='iot', level=logging.INFO):
    logging.basicConfig(level=level,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        filename="/var/log/%s.log" % name,
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
        print >> sys.stderr, 'util move_to_s3 %s' % e.message


def copy_to_s3(from_filename, *args):
    try:
        cmd = ['/usr/bin/aws',
               's3',
               'cp',
               from_filename,
               os.path.join('s3://', *args)]
        pipe = sp.Popen(cmd, stdin=sp.PIPE, stderr=sp.PIPE)  # mv snapshot.png to s3
    except Exception as e:
        print >> sys.stderr, 'util copy_to_s3 %s' % e.message


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
        print >> sys.stderr, 'util annotate_image %s' % e.message


def generate_thumbnail(from_filename, to_filename='thumbnail.png'):
    # generate thumbnail
    # -i input filename
    # -y overwrite thumbnail if exists
    # -vf video filter - let FFmpeg pick best frame
    # -vframes number of frames
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
            print >> sys.stderr, 'generate_thumbnail %s %s %s' % (from_filename, to_filename, ex.message)


def file_name(suffix, *args):
    return '_'.join(args) + '.' + suffix


def full_path(*args):
    return '/'.join(args)


def now_string():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
