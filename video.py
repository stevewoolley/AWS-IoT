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

    def __init__(self,
                 base_filename="output",
                 video_format='h264',
                 horizontal_resolution=640,
                 vertical_resolution=480,
                 rotation=0,
                 path="/tmp",
                 log_level=logging.INFO
                 ):
        threading.Thread.__init__(self)
        self.daemon = True
        self.finish = False
        self.path = path
        self.camera = picamera.PiCamera()
        self.camera.resolution = (horizontal_resolution, vertical_resolution)
        self.camera.rotation = rotation
        self.base_filename = base_filename
        self.recording = False
        self.video_format = video_format
        self.filename = None
        # set logger
        self.logger = util.set_logger(level=log_level)

    def _file_name(self, suffix, prefix=None):
        if prefix is None:
            return "%s.%s" % (self.base_filename, suffix)
        else:
            return "%s-%s.%s" % (prefix, self.base_filename, suffix)

    def _full_path(self, suffix, prefix=None):
        return "%s/%s" % (self.path, self._file_name(suffix, prefix))

    def start_recording(self):
        if not self.recording:
            try:
                self.filename = self._full_path(self.video_format, datetime.now().strftime("%Y-%m-%d_%H.%M.%S"))
                self.camera.start_recording(self.filename, format=self.video_format)
                self.recording = True
            except Exception as ex:
                self.logger.debug('ERROR start_recording %s' % ex.message)
                self.filename = None
                self.recording = False
        return self.recording

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.camera.stop_recording()
            return self.filename
        else:
            return None

    def snapshot(self, snapshot_filename=None):
        try:
            if snapshot_filename is None:
                snapshot_filename = self._full_path('png', datetime.now().strftime("%Y-%m-%d_%H.%M.%S"))
            if self.recording:
                self.camera.capture(snapshot_filename, use_video_port=True)
            else:
                self.camera.capture(snapshot_filename, use_video_port=False)
            return snapshot_filename
        except Exception as ex:
            self.logger.debug('ERROR snapshot %s %s' % (snapshot_filename, ex.message))
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
