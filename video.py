import threading
import time
import picamera
import logging
import util


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

    def start_recording(self):
        if not self.recording:
            try:
                self.filename = util.full_path(self.path, util.file_name(self.video_format, util.now_string()))
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
                snapshot_filename = util.full_path(self.path,
                                                   util.file_name('png', util.now_string()))
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
