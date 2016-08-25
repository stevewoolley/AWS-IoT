import logging
import sys
import os
import subprocess as sp


def set_logger(name='iot', level=logging.INFO):
    logging.basicConfig(level=level,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        filename="/var/log/%s.log" % (name),
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


def move_to_s3(from_filename, *args):
    try:
        cmd = ['/usr/bin/aws',
               's3',
               'mv',
               from_filename,
               os.path.join('s3://', *args)]
        pipe = sp.Popen(cmd, stdin=sp.PIPE, stderr=sp.PIPE)  # mv snapshot.png to s3
    except Exception as e:
        print >> sys.stderr, 'util move_to_s3 %s' % e.message


def annotate_image(filename, msg, font="/usr/share/fonts/truetype/msttcorefonts/arial.ttf", font_size="36",
                   font_color="white", geometry="+50+50"):
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
