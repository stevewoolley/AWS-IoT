import threading
import time
from datetime import datetime
import picamera
import logging
import util
import sys
import subprocess as sp


class Video(threading.Thread):
    """A threaded video object"""
    ON_STRING = 'ON'
    OFF_STRING = 'OFF'

    def __init__(self,
                 filename_prefix='output',
                 filename_suffix='h264',
                 log_level=logging.INFO,
                 video_format='h264',
                 horizontal_resolution=640,
                 vertical_resolution=480,
                 rotation=0,
                 snapshot_filename="snapshot.png"
                 ):
        threading.Thread.__init__(self)
        self.daemon = True
        self.filename_prefix = filename_prefix
        self.filename_suffix = filename_suffix
        self.filename = "%s.%s" % (self.filename_prefix, self.filename_suffix)
        self.recording = False
        self.video_format = video_format
        self.finish = False
        self.snapshot_filename = snapshot_filename
        # initialize camera
        self.horizontal_resolution = horizontal_resolution
        self.vertical_resolution = vertical_resolution
        self.rotation = rotation
        self.camera = picamera.PiCamera()
        self.camera.resolution = (self.horizontal_resolution, self.vertical_resolution)
        self.camera.rotation = self.rotation
        # set logger
        self.logger = util.set_logger(level=log_level)

    def start_recording(self):
        if not self.recording:
            try:
                self.filename = "%s-%s.%s" % (
                    self.filename_prefix, datetime.now().strftime("%Y-%m-%d_%H.%M.%S"), self.filename_suffix)
                self.camera.start_recording(self.filename, format=self.video_format)
                self.recording = True
            except Exception as ex:
                self.logger.debug('ERROR start_recording %s' % ex.message)
                return False
        return self.recording

    def stop_recording(self):
        if self.recording and self.filename:
            self.recording = False
            self.camera.stop_recording()
            return str(self.filename)
        else:
            return None

    def snapshot(self):
        try:
            self.camera.capture(self.snapshot_filename, use_video_port=True)
            return self.snapshot_filename
        except Exception as ex:
            self.logger.debug('ERROR snapshot %s' % ex.message)
            return None

    def run(self):
        while not self.finish:
            time.sleep(.001)

    @staticmethod
    def generate_thumbnail(from_filename, to_filename='thumbnail.png'):
        # generate thumbnail with FFmpeg
        # -i input filename
        # -y overwrite thumbnail if exists
        # -vf video filter - let FFmpeg pick best frame
        # -vframes number of frames
        if from_filename is not None:
            try:
                cmd = ['ffmpegthumbnailer',
                       '-i', from_filename,
                       '-f',
                       '-w',
                       '-s', '0',
                       '-t', '50%',
                       '-o', to_filename]
                time.sleep(0.5)  # give some time to complete file write
                pipe = sp.Popen(cmd, stdin=sp.PIPE, stderr=sp.PIPE)  # write thumbnail.png
            except Exception as ex:
                print >> sys.stderr, 'video.py: generate_thumbnail: %s' % ex.message
